"""Base classes for programs."""

import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from copy import copy
from enum import Enum
from os.path import join
from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from time import sleep, time
from typing import Any, Callable, Iterable, Union

import requests
from appium.webdriver import Remote as RemoteDriver

# https://github.com/ponty/pyscreenshot (past alternative) states that it
# should work on (up-to-date) linux distros (Ubuntu currently: no, Arch currently: yes)
# from PIL import ImageGrab
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

# from threemf_analyzer import LOCAL_SERVER, SFTA_DIR
from threemf_analyzer.dataclasses import DiskFile, File

# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.keys import Keys


# if sys.platform == "win32":
# import win32gui


# set powershell as executable for shell calls
os.environ["COMSPEC"] = "powershell"


class ActionUnsuccessful(Exception):
    """Raised if an action (on a program) was not successful"""


class Be(Enum):
    """State of an element to select."""

    NOTAVAILABLE = "not available"
    AVAILABLE = "available"
    AVAILABLE_NOTENABLED = "available and not enabled"
    AVAILABLE_ENABLED = "available and enabled"


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

    if timed_out and timeout > 0:
        raise ActionUnsuccessful(
            f"Could not finish action: '{action_name}' bacuase it timed out"
        ) from TimeoutExpired(f"Screenshot for {action_name} timed out", timeout=timeout)

    if not successful:
        raise ActionUnsuccessful("Could not finish action: %s")

    return result


class Program(ABC):
    """Abstract Base Class for a single program."""

    def __init__(
        self,
        name: str = None,
        screenshot_timeout: int = 10,
        snapshot_timeout: int = 10,
    ) -> None:
        self.name = name if name is not None else self.__class__.__name__
        self.screenshot_timeout = screenshot_timeout
        self.snapshot_timeout = snapshot_timeout
        self._output_directory = None

    @property
    def output_directory(self) -> str:
        """Returns the currently set output directory for files."""
        return self._output_directory

    @output_directory.setter
    def output_directory(self, path: str) -> None:
        """Sets the output directory where files are written.
        Should be (re-)set for every test case execution."""
        Path(path).mkdir(parents=True, exist_ok=True)
        self.output_directory = path

    @abstractmethod
    def test(
        self,
        file: File,
        output_dir: str,
        program_start_timeout: int = None,
        file_load_timeout: int = None,
    ) -> Iterable[tuple[str, float]]:
        """Start the program with a given file,
        returns only when we think the program has been started and the file is loaded.
        That means this function block while the program is tested.
        It will timeout the loading of the file according to the parameters (infinite if None).
        Return value is a generator of timestamps, with (<name of timestamp>, <time>). Currently:
            <program start loading>
            <program finish loading>/<file start loading>
            <file finish loading>
        Depending on the method of starting the program and loading the file these values might not
        be available, they are None in these cases."""

    @abstractmethod
    def stop(self) -> None:
        """Stops the program execution (send exit signal)."""

    @abstractmethod
    def force_stop_all(self) -> None:
        """Hard kills all currently running instances of this program."""

    @abstractmethod
    def _take_screenshot(self) -> bytes:
        """Takes a screenshot of the program and returns the bytes."""

    def screenshot(self, write_to: DiskFile = None) -> Union[Iterable[DiskFile], Iterable[bytes]]:
        """Takes a screenshot of all open windows of the program and either writes it to the given
        file, or (if not DiskFile was provided) returns the bytes of the screenshot that
        would have been written to the file.
        If no screenshot can be taken, raise ActionUnsuccessful."""

        screenshots = _try_action_until_timeout(
            "take screenshot", self._take_screenshot, self.screenshot_timeout
        )

        if write_to is not None:
            for number, screenshot in enumerate(screenshots):
                res = copy(write_to)
                res.stem += f"_{number}"
                res.content = screenshot
                yield res
        else:
            yield from screenshot

    @abstractmethod
    def _take_snapshot(self) -> bytes:
        """Takes a screenshot of the program and returns the bytes."""

    def snapshot(self, write_path: str = None) -> Union[None, dict]:
        """Takes a snapshot of the current program state and either writes it to the given file,
        or (if not path was provided) returns the dict-representation of the data that
        would have been written to the file.
        If no snapshot can be taken, raise ActionUnsuccessful"""

        snapshot = _try_action_until_timeout(
            "take snapshot", self._take_snapshot, self.snapshot_timeout
        )

        if write_path is not None:
            with open(write_path, "wb") as out_file:
                out_file.write(snapshot)
        else:
            return json.loads(snapshot.decode("utf-8", "ignore"))


class WinAppDriverProgram(Program):
    """Program that is controlled by the WinAppDriver.
    This class offers general functions for this control method."""

    def __init__(
        self,
        name: str,
        executable_path: str,
        process_name: str,
        status_change_names: dict[str, list[str]],
        screenshot_timeout: int = 10,
        snapshot_timeout: int = 10,
    ) -> None:
        """
        program_loaded_name defines the name of an element in the GUI that is always there.
            this is used to detect whether the program was fully loaded or not.
        model_loaded_name is the same for an element that is there once the model object is loaded.
        """
        super().__init__(name, screenshot_timeout, snapshot_timeout)
        self.executable_path = executable_path
        self.process_name = process_name
        self.status_change_names = status_change_names
        self.driver: RemoteDriver = None

    def __find_elements(self, names: dict[str, list[tuple[By, str, Be]]]):
        """Finds an element in any window associated with the process.
        The driver focuses the window where the element was first found after this."""
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            for change_type, values in names.items():
                for by, name, expect in values:
                    try:
                        element = self.driver.find_element(by, name)
                    except WebDriverException:
                        element = None
                    if element is None and expect == Be.NOTAVAILABLE:
                        return change_type
                    if element is not None:
                        element: WebElement
                        if (
                            (expect == Be.AVAILABLE)
                            or (expect == Be.AVAILABLE_ENABLED and element.is_enabled())
                            or (expect == Be.AVAILABLE_NOTENABLED and not element.is_enabled())
                        ):
                            return change_type

        raise WebDriverException("Cannot find any of the elements in any window")

    def _wait_for_change(self, names: dict[str, list[tuple[By, str]]], timeout: int = 30) -> str:
        """Busy-waits while the program is loading something.

        Uses the strings in <names> to determine whether the program state changed accordingly.
        This searches all windows associated with the process for said string and focuses the
        window where the string was found as an element. Make sure that the names are unique
        to the window that you want to screenshot, otherwise this might not work as expected.

        <names> is { <type of change> : <name of element detected> } where the type of change is a
        string that is used as an id (returned to you so you know what happened).

        Times out it no element was found in any window after <timeout> seconds."""

        return _try_action_until_timeout(
            "detect change",
            lambda: self.__find_elements(names),
            timeout,
            catch=(WebDriverException,),
            rate=1,
        )

    def _transform_status_names(self, keys: list[str], format_values: dict[str, str] = None):
        """Creates a new dict with only the given keys, if they are in the original.
        Formats each value string of this the input dict with the values from the format_values dict,
        if given."""
        if format_values is None:
            return {k: self.status_change_names[k] for k in keys if k in self.status_change_names}

        result = {}
        for k in keys:
            if k in self.status_change_names:
                result[k] = []
                for (identifier, value, expect) in self.status_change_names[k]:
                    result[k].append((identifier, value.format(**format_values), expect))
        return result

    def _start_program(self):
        """Starts the program without CLI arguments."""
        self.driver = RemoteDriver(
            command_executor="http://127.0.0.1:4723",
            desired_capabilities={"app": self.executable_path},
        )

    def _wait_program_load(self, model: File, program_start_timeout: int):
        """Busy-wait for the program to load."""
        self._wait_for_change(
            names=self._transform_status_names(
                ["program loaded"],
                {
                    "abspath": model.abspath,
                    "name": model.name,
                    "stem": model.stem,
                },
            ),
            timeout=program_start_timeout,
        )

    @abstractmethod
    def _load_model(self, model: File):
        """Loads the model file in the program."""

    def _wait_model_load(self, model: File, file_load_timeout: int):
        """Busy-wait for the model to load.
        ActionUnsuccessful is raised if the model cannot be loaded."""
        change_type = self._wait_for_change(
            names=self._transform_status_names(
                ["file loaded", "error"],
                {
                    "abspath": model.abspath,
                    "name": model.name,
                    "stem": model.stem,
                },
            ),
            timeout=file_load_timeout,
        )
        if change_type == "error":
            raise ActionUnsuccessful("error msg detected in window")

    def test(
        self,
        file: File,
        output_dir: str,
        program_start_timeout: int = 60,
        file_load_timeout: int = 30,
    ) -> Iterable[tuple[str, float, Iterable[DiskFile]]]:

        self.force_stop_all()

        def __create_timestamp(name: str, take_screenshot: bool = True):
            current_time = time()
            if not take_screenshot:
                return (name, current_time, [])
            try:
                screenshots = list(
                    self.screenshot(
                        write_to=DiskFile(
                            stem=f"screenshot_{name.replace(' ','_')}",
                            extension="png",
                            abspath=output_dir,
                        )
                    )
                )
            except ActionUnsuccessful as err:
                logging.error(
                    "Tried to take screenshot for timestamp '%s', but failed with '%s'", name, err
                )
                screenshots = []
            return (name, current_time, screenshots)

        yield __create_timestamp("01 start-program", take_screenshot=False)

        self._start_program()

        try:
            self._wait_program_load(file, program_start_timeout)
        except ActionUnsuccessful as err:
            logging.error("program not loaded, because: %s", err)
            yield __create_timestamp("02 program-not-loaded")
            return
        else:
            yield __create_timestamp("02 program-loaded")

        self.driver.switch_to.window(self.driver.current_window_handle)  # focus window

        yield __create_timestamp("03 start-file-loading", take_screenshot=False)

        self._load_model(model=file)

        try:
            self._wait_model_load(file, file_load_timeout)
        except ActionUnsuccessful as err:
            logging.error("model not loaded, because: %s", err)
            yield __create_timestamp("04 model-not-loaded")
        else:
            yield __create_timestamp("04 model-loaded")

        self.stop()

    def stop(self) -> None:
        self.driver.quit()

    def force_stop_all(self) -> None:
        _stop_process(self.process_name)

    def _take_screenshot(self) -> Union[bytes, Iterable[bytes]]:
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            yield self.driver.get_screenshot_as_png()

    def _take_snapshot(self) -> bytes:
        finished_proc = _run_ps_command(
            ["Get-Process", "-Name", self.process_name, "|", "ConvertTo-Json"]
        )
        return finished_proc.stdout


class DefaultWinAppDriverProgram(WinAppDriverProgram):
    """WinAppDriverProgram with a default load_model function and
    an additional init parameter."""

    def __init__(
        self,
        name: str,
        executable_path: str,
        process_name: str,
        status_change_names: dict[str, list[str]],
        open_file_dialogue_keys: str,
        screenshot_timeout: int = 10,
        snapshot_timeout: int = 10,
    ) -> None:
        super().__init__(
            name,
            executable_path,
            process_name,
            status_change_names,
            screenshot_timeout,
            snapshot_timeout,
        )
        self.open_file_dialogue_keys = open_file_dialogue_keys

    def _load_model(self, model: File):
        ActionChains(self.driver).send_keys(self.open_file_dialogue_keys).perform()
        sleep(2)
        self.driver.find_element_by_name("File name:").click()
        ActionChains(self.driver).send_keys(model.abspath).perform()
        ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()


# class PowerShellProgram(Program):
#     """Program that is controlled via PowerShell/CLI commands.
#     This class offers general functions for this control method.

#     Attributes:
#         pid (str): The internal ID for a program,
#             is also used as file/folder name where appropriate.
#         name (str): Printable name of the program.
#         association_id (str): The ID given by Windows, this is used in the SFTA script.
#             The ID can be found by the Get-FTA function from the SFTA script as well.
#         exec_path (str): Path to the executable (.exe) to be executed directly instead of through
#             type associations.
#         process_name (str): The name of the process when running.
#             Among others, used to kill the program.
#         window_title (str): Format string version of the window's title.
#             This is used to identify the window to obtain a screenshot.
#             The string has to occur in the window's title and should be as exact as possible,
#             as not to select another window.
#             If not explicitly given is the same as the name.
#             Supported format string variables are:
#             - filename: Name of the currently processed file
#             - filename_ext: Name of the currently processed file with extension
#             - program_name: name variable of this object
#             - process_name: process_name variable of this object
#     """

#     def __init__(
#         self,
#         pid,
#         name,
#         association_id,
#         exec_path,
#         process_name,
#         window_title,
#     ) -> None:
#         super().__init__(name, ..., ...)
#         self.pid: str = pid
#         self.association_id: str = association_id
#         self.exec_path: str = exec_path
#         self.process_name: str = process_name
#         self.window_title: str = window_title
#         self.hwnd: int = None

#     def _set_association_id(self, timeout: int = 10) -> None:
#         """Sets the current (Windows-wide) association ID for 3MF files
#         to the ID of the current program.

#         As there is a weird bug, where sometimes ideaMaker is (falsely) set as the associated
#         program check before setting if the ID is still correct and then set the ID as often as
#         necessary until it is correct."""

#         def _get_current_id():
#             return (
#                 _run_ps_command(["& { . .\\SFTA.ps1; Get-FTA .3mf }"], cwd=SFTA_DIR)
#                 .stdout.decode("utf-8")
#                 .strip()
#             )

#         start_time = time()
#         timed_out = False
#         while _get_current_id() != self.association_id and not timed_out:
#             _run_ps_command(
#                 [f"& {{ . .\\SFTA.ps1; Set-FTA {self.association_id} .3mf }}"],
#                 cwd=SFTA_DIR,
#             )
#             timed_out = time() - start_time > timeout
#         if timed_out:
#             raise TimeoutExpired("Set association ID", timeout=timeout)

#     def _start(
#         self,
#         file: File,
#         program_start_timeout: int = None,
#         file_load_timeout: int = None,
#     ) -> tuple[float, float, float]:
#         if self.exec_path is not None:
#             _run_ps_command(
#                 ["Start-Process", "-FilePath", self.exec_path, "-ArgumentList", file.abspath],
#                 timeout=program_start_timeout,
#             )

#         elif self.association_id is not None:
#             # set the File Type Association to use the given program
#             # we do it this way, as the apps installed from the windows store
#             # (currently paint 3d and 3d builder) do not allow to be
#             # started given a file from the command line
#             # this approach should(tm) work universally
#             self._set_association_id(self.association_id)
#             _run_ps_command(
#                 ["Start-Process", "-FilePath", file.abspath],
#                 timeout=program_start_timeout,
#             )

#         else:
#             raise ValueError(
#                 f"Program {self} must have either set exec_path or type_association_id"
#             )

#         return time()

#     def start_test(
#         self,
#         file: File,
#         program_start_timeout: int = None,
#         file_load_timeout: int = None,
#     ) -> tuple[float, float, float]:
#         self._start

#     def stop(self) -> None:
#         self.force_stop_all()

#     def force_stop_all(self) -> None:
#         _stop_process(self.process_name)

#     def _get_window_handle(self, timeout: int = 0) -> int:
#         """
#         Get the window handle from the process information, busy waits for the window to be ready.
#         Raises error if window not ready in `timeout` seconds.
#         timeout = 0 expects that the window exists and can be found at the first try.
#         """

#         def _get_windows_by_title():
#             """Based on: https://stackoverflow.com/a/3278356 (c) 2010 KobeJohn"""

#             def _window_callback(hwnd, all_windows):
#                 all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

#             windows = []
#             win32gui.EnumWindows(_window_callback, windows)
#             handles = [hwnd for hwnd, title in windows if self.window_title in title and hwnd != 0]
#             if handles:
#                 return handles[0]

#         def _get_windows_by_process():
#             try:
#                 finished_proc = _run_ps_command(
#                     ["Get-Process", "-Name", self.process_name, "|", "ConvertTo-Json"]
#                 )
#             except:  # pylint:disable = bare-except
#                 return
#             res = json.loads(finished_proc.stdout.decode("utf-8", "ignore"))
#             if isinstance(res, list):
#                 res = res[0]
#             if res.get("MainWindowHandle") != "0" and self.window_title in res.get(
#                 "MainWindowTitle", ""
#             ):
#                 return res.get("MainWindowHandle")

#         hwnd = None
#         start_time = time()
#         timed_out = False

#         while not hwnd and not timed_out:
#             hwnd = _get_windows_by_process()
#             logging.debug("hwnd after by_process retrieval: %s", hwnd)
#             if not hwnd:
#                 hwnd = _get_windows_by_title()
#                 logging.debug("hwnd after by_title retrieval: %s", hwnd)
#             timed_out = time() - start_time > timeout
#             sleep(0.1)

#         if timed_out and timeout > 0:
#             raise TimeoutExpired("Window handel retrieval timed out", timeout=timeout)

#         if not hwnd:
#             raise ValueError("Couldn't find window handle number")

#         return hwnd

#     def _take_screenshot(self) -> bytes:
#         bounding_box = left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
#         if abs(right - left) < 500 and abs(bottom - top) < 500:
#             # if screenshot to small, take whole screen
#             bounding_box = None
#         image = ImageGrab.grab(bbox=bounding_box)
#         output = BytesIO()
#         image.save(output, format="PNG")
#         return output.read()

#     def screenshot(self, write_path: str = None) -> Union[None, bytes]:
#         self.hwnd = self._get_window_handle()
#         return super().screenshot(write_path)

#     def _take_snapshot(self) -> bytes:
#         finished_proc = _run_ps_command(
#             ["Get-Process", "-Name", self.process_name, "|", "ConvertTo-Json"]
#         )
#         return finished_proc.stdout
