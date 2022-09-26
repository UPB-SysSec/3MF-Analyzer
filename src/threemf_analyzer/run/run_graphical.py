"""
Runs the build and described tests in /build and /data/description/*.yaml
on the programs defined in /data/programs/config.yaml.
The screenshots of the execution are stored in the evaluation folder of the program
in a folder called `screenshots`.
"""

# pylint: disable=bare-except,broad-except

import json
import logging
import os
import subprocess
from os.path import join
from subprocess import CalledProcessError, CompletedProcess, TimeoutExpired
from time import sleep, time
from typing import Dict, List, Union

# if sys.platform == "win32":
import win32gui

# https://github.com/ponty/pyscreenshot (past alternative) states that it
# should work on (up-to-date) linux distros (Ubuntu currently: no, Arch currently: yes)
from PIL import ImageGrab

from .. import SFTA_DIR, yaml
from ..dataclasses import File, Program
from .run_tests import switch_server_logfile

# set powershell as executable for shell calls
os.environ["COMSPEC"] = "powershell"


def _run_ps_command(
    command: List[str],
    cwd: str = None,
    check: bool = True,
    timeout: float = None,
) -> CompletedProcess:
    """Runs a given command in powershell."""
    logging.debug("Calling command: %s", command)

    return subprocess.run(
        command,
        capture_output=True,
        check=check,
        cwd=cwd,
        timeout=timeout,
        shell=True,
    )


def _set_association_id(association_id: str, timeout: int = 10) -> None:
    """Sets the current (Windows-wide) association ID for 3MF files to the given ID.

    As there is a weird bug, where sometimes ideaMaker is (falsely) set as the associated program
    check before setting if the ID is still correct and then set the ID as often as necessary until
    it is correct."""

    def _get_current_id():
        return (
            _run_ps_command(["& { . .\\SFTA.ps1; Get-FTA .3mf }"], cwd=SFTA_DIR)
            .stdout.decode("utf-8")
            .strip()
        )

    start_time = time()
    timed_out = False
    while _get_current_id() != association_id and not timed_out:
        _run_ps_command(
            [f"& {{ . .\\SFTA.ps1; Set-FTA {association_id} .3mf }}"],
            cwd=SFTA_DIR,
        )
        timed_out = time() - start_time > timeout
    if timed_out:
        raise TimeoutExpired("Set association ID", timeout=timeout)


def _start_program(program: Program, file: File) -> float:
    """Starts a program with the given file.

    program: dict
    file: dict

    return: start time"""

    if program.exec_path is not None:
        _run_ps_command(
            ["Start-Process", "-FilePath", program.exec_path, "-ArgumentList", file.abspath]
        )

    elif program.type_association_id is not None:
        # set the File Type Association to use the given program
        # we do it this way, as the apps installed from the windows store
        # (currently paint 3d and 3d builder) do not allow to be
        # started given a file from the command line
        # this approach should(tm) work universally
        _set_association_id(program.type_association_id)
        _run_ps_command(["Start-Process", "-FilePath", file.abspath])

    else:
        raise ValueError(f"Program {program} must have either set exec_path or type_association_id")

    return time()


def stop(program: Program) -> None:
    _run_ps_command(["Stop-Process", "-Name", program.process_name], check=False)


def _stop_program(program: Program, output_dir: str, output_filestem: str) -> None:
    """Stops a program"""

    try:
        _finished_proc = _run_ps_command(
            ["Get-Process", "-Name", program.process_name, "|", "ConvertTo-Json"]
        )
        res = json.loads(_finished_proc.stdout.decode("utf-8", "ignore"))
        if isinstance(res, list):
            # if list take the process with the highest base priority
            processes_desc_order = sorted(res, key=lambda x: x["BasePriority"], reverse=True)
            res = processes_desc_order[0]

        pid = res.get("Id")

        finished_proc = _run_ps_command(
            ["$p", "=", "Get-Process", "-Id", f"{pid}", ";"]
            + ["Stop-Process", "-Name", program.process_name, ";"]
            + ["$p", "|", "ConvertTo-Json"],
            timeout=30,
        )

    except TimeoutExpired:
        logging.error("Failed to get process infos at process stop. %s", program.name)
        stop(program)
        return

    with open(join(output_dir, f"{output_filestem}.json"), "wb") as out_file:
        out_file.write(finished_proc.stdout)


def _make_screenshot(hwnd: int, output_dir: str, output_filestem: str) -> None:
    """Makes a screenshot of the given program"""
    bounding_box = left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    if abs(right - left) < 500 and abs(bottom - top) < 500:
        # if screengrab to small, take whole screen
        bounding_box = None
    image = ImageGrab.grab(bbox=bounding_box)
    output_filepath = join(output_dir, f"{output_filestem}.png")
    image.save(output_filepath, format="PNG")


def _get_process_infos(
    program: Program,
    output_dir: str,
    output_filestem: str,
    timeout: int = 0,
) -> None:
    successful = False
    start_time = time()
    timed_out = False
    while not successful and not timed_out:
        try:
            finished_proc = _run_ps_command(
                ["Get-Process", "-Name", program.process_name, "|", "ConvertTo-Json"]
            )
            successful = True
        except CalledProcessError as err:
            logging.debug(
                "Process information retrieval unsuccessful: %s %s\nstdout: %s\nstderr: %s",
                program.name,
                output_filestem,
                err.stdout,
                err.stderr,
            )
        timed_out = time() - start_time > timeout
        sleep(0.1)

    if timed_out and timeout > 0:
        raise TimeoutExpired(
            f"Process information retrieval for {output_filestem} timed out", timeout=timeout
        )

    if not successful:
        return {
            "company": "",
            "version": "",
            "product": program.name,
        }

    if output_dir is not None:
        with open(join(output_dir, f"{output_filestem}.json"), "wb") as out_file:
            out_file.write(finished_proc.stdout)

    res = json.loads(finished_proc.stdout.decode("utf-8", "ignore"))
    if isinstance(res, list):
        res = res[0]
    return {
        "company": res.get("Company", ""),
        "version": res.get("ProductVersion", "0"),
        "product": res.get("Product", ""),
    }


def _get_window_handle(program: Program, window_title: str, timeout: int = 0) -> int:
    """Get the window handle from the process information, busy waits for the window to be ready.
    Raises error if window not ready in `timeout` seconds.
    timeout = 0 expects that the window exists and can be found at the first try."""

    def _get_windows_by_title():
        """Based on: https://stackoverflow.com/a/3278356 (c) 2010 KobeJohn"""

        def _window_callback(hwnd, all_windows):
            all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

        windows = []
        win32gui.EnumWindows(_window_callback, windows)
        handles = [hwnd for hwnd, title in windows if window_title in title and hwnd != 0]
        if handles:
            return handles[0]

    def _get_windows_by_process():
        try:
            finished_proc = _run_ps_command(
                ["Get-Process", "-Name", program.process_name, "|", "ConvertTo-Json"]
            )
        except:
            return
        res = json.loads(finished_proc.stdout.decode("utf-8", "ignore"))
        if isinstance(res, list):
            res = res[0]
        if res.get("MainWindowHandle") != "0" and window_title in res.get("MainWindowTitle", ""):
            return res.get("MainWindowHandle")

    hwnd = None
    start_time = time()
    timed_out = False

    while not hwnd and not timed_out:
        hwnd = _get_windows_by_process()
        logging.debug("hwnd after by_process retrieval: %s", hwnd)
        if not hwnd:
            hwnd = _get_windows_by_title()
            logging.debug("hwnd after by_title retrieval: %s", hwnd)
        timed_out = time() - start_time > timeout
        sleep(0.1)

    if timed_out and timeout > 0:
        raise TimeoutExpired("Window handel retrieval timed out", timeout=timeout)

    if not hwnd:
        raise ValueError("Couldn't find window handle number")

    return hwnd


def test_program_on_file(
    snapshot_intervals: List[int],
    program: Program,
    file: File,
    output_dir: str,
    process_startup_timeout: int = 30,
    window_startup_timeout: int = 30,
) -> Union[None, Dict[str, Dict[str, str]]]:
    """Runs a program with the given file and creates screenshots of the result."""

    window_title = program.window_title.format(
        filename=file.stem,
        filename_ext=file.name,
        program_name=program.name,
        process_name=program.process_name,
    )
    logging.debug("Window title that is used to get the window handler: %s", window_title)
    with open(join(output_dir, "snapshot_intervals.txt"), "w", encoding="utf-8") as outfile:
        outfile.write(",".join(map(str, snapshot_intervals)))

    try:
        switch_server_logfile(program, file, output_dir)
        _start_program(program, file)
        program_infos = _get_process_infos(
            program, output_dir, "00_at-init", timeout=process_startup_timeout
        )
    except TimeoutExpired:
        with open(join(output_dir, "error-info.txt"), "w", encoding="utf-8") as outfile:
            outfile.write(f"Process did not start in {process_startup_timeout} seconds.")
        raise

    try:
        try:
            hwnd = _get_window_handle(program, window_title, timeout=window_startup_timeout)
            logging.debug("%s window detected. start timer", program.name)
        except TimeoutExpired:
            with open(join(output_dir, "error-info.txt"), "w", encoding="utf-8") as outfile:
                outfile.write(f"Window did not start in {window_startup_timeout} seconds.")
            raise

        start_time = time()  # start time of window appearance
        for number, timeinterval in enumerate(snapshot_intervals):
            while time() - start_time < timeinterval:
                sleep(0.1)

            try:
                hwnd = _get_window_handle(program, window_title)
            except:
                pass
            output_filestem = f"{number+1:02}_{timeinterval}s-after-start"
            try:
                _get_process_infos(program, output_dir, output_filestem)
            except Exception as err:
                logging.error(
                    "Failed to get process infos. %s: %s, %s\n%s",
                    program.name,
                    file.test_id,
                    output_filestem,
                    err,
                )
            try:
                _make_screenshot(hwnd, output_dir, output_filestem)
            except Exception as err:
                logging.error(
                    "Failed to take screenshot. %s: %s, %s\n%s",
                    program.name,
                    file.test_id,
                    output_filestem,
                    err,
                )

    except:
        _get_process_infos(program, output_dir, "98_before-stop")
        raise

    finally:
        _stop_program(program, output_dir, "99_after-stop")

    return program_infos
