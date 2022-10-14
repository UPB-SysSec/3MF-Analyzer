import logging
import shutil
import sys
import traceback
from os.path import isdir, join
from pathlib import Path

import requests

from .. import EVALUATION_DIR, LOCAL_SERVER
from ..dataclasses import File
from .arg_parser import sanitize_args
from .programs.base import Program
from .update_evaluation_info import modify_all_eval_info
from .verify_results import verify_results


def switch_server_logfile(program: Program, file: File, output_dir: str) -> None:
    """Utility function that sends a POST request to the logging server
    to set the logfile location."""

    logfile_path = join(output_dir, "local-server.log")
    log_init_msg = f"Start server log for {program.name} running {file.test_id}"
    try:
        req = requests.post(LOCAL_SERVER, json={"logfile": logfile_path}, timeout=5)
        if req.status_code != 200:
            raise requests.ConnectionError()
        logging.debug("Send post to set logfile path to %s", logfile_path)
        requests.get(LOCAL_SERVER + "/" + log_init_msg, timeout=5)
    except requests.RequestException:
        logging.warning("Logging server seems unresponsive")


def _run_program(
    program_cls: type[Program],
    files: list[File],
    run_flag: bool,
    clear_flag: bool,
):
    program_dir = join(EVALUATION_DIR, program_cls().name)

    for file in files:
        try:
            output_dir = join(program_dir, "snapshots", file.test_id)
            if clear_flag and isdir(output_dir):
                logging.debug("Removing directory: %s", output_dir)
                shutil.rmtree(output_dir)
            if run_flag:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                program: Program = program_cls()
                switch_server_logfile(program, file, output_dir)

                logging.info("Testing %s with %s (%s)", program.name, file.stem, file.name)
                for state, timestamp in program.test(file=file, output_dir=output_dir):
                    logging.info("======= %s %s", state, timestamp)

        except Exception as err:  # pylint:disable = broad-except
            logging.error("Error while testing %s with %s: %s", program.name, file.name, err)
            traceback.print_tb(err.__traceback__)

    if run_flag:
        program_cls().force_stop_all()


def run_tests(parsed_arguments: dict[str, str]) -> None:
    programs, files = sanitize_args(parsed_arguments)
    logging.info("Processed arguments:\n  programs=%s\n  files=%s", programs, files)

    # indicates whether or not the tests are executed
    run_flag = not parsed_arguments.get("clear")
    # indicates whether or not the directories are cleared
    clear_flag = parsed_arguments.get("clear") or parsed_arguments.get("clear_and_run")

    if run_flag and sys.platform != "win32" and not parsed_arguments.get("data_update_only"):
        raise ValueError("Executing/Running the tests only works on Windows!")

    if not parsed_arguments.get("data_update_only"):
        for program in programs:
            _run_program(program, files, run_flag, clear_flag)

    verification_results = verify_results(programs, files)
    modify_all_eval_info(verification_results)
