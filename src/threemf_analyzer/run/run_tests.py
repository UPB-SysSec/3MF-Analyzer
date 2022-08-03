import logging
import shutil
import sys
import traceback
from os.path import isdir, join
from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired
from typing import Dict, List, Union

import requests

from .. import EVALUATION_DIR, LOCAL_SERVER
from ..dataclasses import File, Program
from .arg_parser import sanitize_args
from .update_evaluation_info import modify_all_eval_info
from .verify_results import verify_results


def switch_server_logfile(program: Program, file: File, output_dir: str) -> None:
    """Utility function that sends a POST reqest to the logging server
    to set the logfile location."""

    logfile_path = join(output_dir, "local-server.log")
    log_init_msg = f"Start server log for {program.name} running {file.test_id}"
    try:
        r = requests.post(LOCAL_SERVER, json={"logfile": logfile_path})
        if r.status_code != 200:
            raise requests.ConnectionError()
        logging.debug("Send post to set logfile path to %s", logfile_path)
        requests.get(LOCAL_SERVER + "/" + log_init_msg)
    except requests.RequestException:
        logging.warning("Logging server seems unresponsive")


def _run_program(
    program: Program,
    files: List[File],
    snapshot_intervals: List[int],
    run_flag: bool,
    clear_flag: bool,
    parsed_arguments: Dict[str, str],
):
    if program.id == "lib3mf":
        from .run_libtmf import stop, test_program_on_file
    else:
        from .run_graphical import stop, test_program_on_file
    program_dir = join(EVALUATION_DIR, program.id)
    program_infos = {
        "company": "",
        "version": "",
        "product": "",
    }

    for file in files:
        try:
            output_dir = join(program_dir, "snapshots", file.test_id)
            if clear_flag and isdir(output_dir):
                logging.debug("Removing directory: %s", output_dir)
                shutil.rmtree(output_dir)
            if run_flag:
                Path(output_dir).mkdir(parents=True, exist_ok=True)

                stop(program)  # stop eventually running instances
                logging.info("Testing %s with %s (%s)", program.name, file.stem, file.name)
                _program_infos = test_program_on_file(
                    snapshot_intervals=snapshot_intervals,
                    program=program,
                    file=file,
                    output_dir=output_dir,
                    process_startup_timeout=parsed_arguments.get("process_startup_timeout"),
                    window_startup_timeout=parsed_arguments.get("window_startup_timeout"),
                )
                for key, val in _program_infos.items():
                    if program_infos.get(key, "") == "":
                        program_infos[key] = val
        except CalledProcessError as err:
            logging.error(
                "Error while testing %s with %s: %s\nstdout: %s\nstderr: %s",
                program.name,
                file.name,
                err,
                err.stdout,
                err.stderr,
            )
        except Exception as err:
            logging.error("Error while testing %s with %s: %s", program.name, file.name, err)
            traceback.print_tb(err.__traceback__)
        finally:
            if run_flag:
                stop(program)

    return program_infos


def run_tests(parsed_arguments: Dict[str, str]) -> None:
    snapshot_intervals, programs, files = sanitize_args(parsed_arguments)
    logging.info(f"Processed arguments:\n  {programs=}\n  {files=}\n  {snapshot_intervals=}")

    # indicates whether or not the tests are executed
    run_flag = not parsed_arguments.get("clear")
    # indicates whether or not the directories are cleared
    clear_flag = parsed_arguments.get("clear") or parsed_arguments.get("clear_and_run")

    if run_flag and sys.platform != "win32" and not parsed_arguments.get("data_update_only"):
        raise ValueError("Exectuting/Running the tests only works on Windows!")

    programs_infos = {}

    if not parsed_arguments.get("data_update_only"):
        for program in programs:
            programs_infos[program] = _run_program(
                program, files, snapshot_intervals, run_flag, clear_flag, parsed_arguments
            )
    # else:
    #     for program in programs:
    #         _start_program(program, files[0])
    #         sleep(2)
    #         programs_infos[program.id] = _get_process_infos(program, None, "info_gathering_run")
    #         _simple_stop(program)

    # logging.debug("Program information: %s", programs_infos)
    verification_results = verify_results(programs, files)
    modify_all_eval_info(verification_results, programs_infos, programs)
