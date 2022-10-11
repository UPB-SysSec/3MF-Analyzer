"""Utility functions for program implementation."""

import logging
import os
import subprocess
from subprocess import CompletedProcess, TimeoutExpired
from time import sleep, time
from typing import Any, Callable

from .utilclasses import ActionUnsuccessful

# from threemf_analyzer import LOCAL_SERVER

os.environ["COMSPEC"] = "powershell"  # set powershell as executable for shell calls

# def _switch_server_logfile(program: "Program", file: File, output_dir: str) -> None:
#     """Utility function that sends a POST request to the logging server
#     to set the logfile location."""

#     logfile_path = join(output_dir, "local-server.log")
#     log_init_msg = f"Start server log for {program.name} running {file.test_id}"
#     try:
#         result = requests.post(LOCAL_SERVER, json={"logfile": logfile_path}, timeout=10)
#         if result.status_code != 200:
#             raise requests.ConnectionError()
#         logging.debug("Send post to set logfile path to %s", logfile_path)
#         requests.get(LOCAL_SERVER + "/" + log_init_msg, timeout=10)
#     except requests.RequestException:
#         logging.warning("Logging server seems unresponsive")


def _run_ps_command(
    command: list[str],
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


def _stop_process(process_name: str):
    _run_ps_command(["Stop-Process", "-Name", process_name], check=False)


def _try_action_until_timeout(
    action_name: str,
    action: Callable,
    timeout: int,
    catch: tuple[type[Exception]] = (Exception,),
    rate: float = 0.1,
) -> Any:
    """Tries to do an action until it succeeds (i.e. does not raise an error)
    or until the timeout runs out.
    Returns whatever the action returns.
    Rate is the time the process sleeps before trying to do the action again."""
    successful = False
    start_time = time()
    timed_out = False
    while not successful and not timed_out:
        try:
            result = action()
            successful = True
        except catch as err:  # pylint:disable = broad-except
            logging.debug(
                "Could not finish action: %s\n%s",
                action_name,
                err,
            )
        timed_out = time() - start_time > timeout
        sleep(rate)

    if successful:
        return result

    if timed_out and timeout > 0:
        raise ActionUnsuccessful(
            f"Could not finish action: '{action_name}' because it timed out"
        ) from TimeoutExpired(f"Screenshot for {action_name} timed out", timeout=timeout)

    if not successful:
        raise ActionUnsuccessful("Could not finish action: %s")

    return result
