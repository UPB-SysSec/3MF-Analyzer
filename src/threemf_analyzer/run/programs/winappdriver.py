"""Base classes for programs."""

import atexit
import logging
import shutil
import sys
import tempfile
from abc import ABCMeta, abstractmethod
from pathlib import Path
from time import sleep
from typing import Any, Iterable, Union

import easyocr
from appium.webdriver import Remote as RemoteDriver
from PIL import Image
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from ...dataclasses import DiskFile, File
from ...evaluate.screenshots import _compare_images, _convert_image_to_ndarray
from .base import Program
from .utilclasses import (
    Action,
    ActionUnsuccessful,
    Be,
    By,
    Capabilities,
    Context,
    ExpectElement,
    State,
)
from .utils import _run_ps_command, _stop_process, _try_action_until_timeout

if sys.platform == "win32":
    import win32gui

    # load easyocr reader (done only on windows because it is so slow and we only need it there)
    OCR_READER = easyocr.Reader(["en"])

    try:
        _driver = RemoteDriver(
            command_executor="http://127.0.0.1:4723",
            desired_capabilities={"app": "Root"},
        )
        if _driver:
            _driver.quit()
    except WebDriverException as _err:
        raise ImportError("WinAppDriver is not able to connect. It needs to be running!") from _err
    del _driver


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
        self.root: RemoteDriver = None

    def _get_context(self, context: Context) -> RemoteDriver:
        """Returns the matching session for the required context."""
        if context == Context.ROOT:
            return self.root
        if context == Context.SELF:
            return self.driver

    def _find_elements(
        self,
        names: dict[str, list[ExpectElement]],
        return_change_type: bool = True,
    ):
        """Finds an element in any window associated with the process.
        The driver focuses the window where the element was first found after this.
        If return_change_type is False whatever type of element was found is returned."""

        def __by_ocr(element: ExpectElement):
            logging.info("Try to find '%s' using OCR", element.value)
            target = self._text_on_screen(element)
            if target is True and element.expect == Be.AVAILABLE:
                logging.info("Found '%s' using OCR", element.value)
                return change_type if return_change_type else element.value
            elif target is False and element.expect == Be.NOTAVAILABLE:
                logging.info("Did not find '%s' using OCR", element.value)
                return change_type if return_change_type else element.value

        def __by_wad(element: ExpectElement):
            try:
                current_parent = self._get_context(element.context)
                if element.parents:
                    current_parent = self._get_context(element.parents[0].context)
                logging.debug("Using WinAppDriver: %s", current_parent)
                for parent_element in element.parents:
                    current_parent = current_parent.find_element(
                        parent_element.by, parent_element.value
                    )
                logging.info("Try to find '%s' using '%s'", element, current_parent)
                target = current_parent.find_element(element.by, element.value)
            except WebDriverException:
                target = None
            if target is None and element.expect == Be.NOTAVAILABLE:
                return change_type if return_change_type else target
            if target is not None:
                target: WebElement
                if (
                    (element.expect == Be.AVAILABLE)
                    or (element.expect == Be.AVAILABLE_ENABLED and target.is_enabled())
                    or (element.expect == Be.AVAILABLE_NOTENABLED and not target.is_enabled())
                ):
                    return change_type if return_change_type else target

        for change_type, elements in names.items():
            for element in elements:

                if element.by == By.OCR:
                    exec_func = __by_ocr
                else:
                    exec_func = __by_wad

                if handles := self.driver.window_handles:
                    for handle in handles:
                        self.driver.switch_to.window(handle)
                        if (result := exec_func(element)) is not None:
                            return result
                        else:
                            continue
                else:
                    if (result := exec_func(element)) is not None:
                        return result
                    else:
                        continue

        raise WebDriverException("Cannot find any of the elements in any window")

    def _get_format_strings(self, model: File):
        """Returns a dict of format strings for the current model
        to be used in the find_elements strings."""
        return {
            "abspath": model.abspath,
            "abspath_unix": model.abspath.replace("\\", "/"),
            "name": model.name,
            "stem": model.stem,
        }

    def _wait_for_change(
        self,
        names: dict[str, list[ExpectElement]],
        timeout: int = 30,
        return_change_type: bool = True,
    ) -> str:
        """Busy-waits while the program is loading something.

        Uses the strings in <names> to determine whether the program state changed accordingly.
        This searches all windows associated with the process for said string and focuses the
        window where the string was found as an element. Make sure that the names are unique
        to the window that you want to screenshot, otherwise this might not work as expected.

        <names> is { <type of change> : <name of element detected> } where the type of change is a
        string that is used as an id (returned to you so you know what happened).

        Times out it no element was found in any window after <timeout> seconds."""

        logging.debug("started 'detect change' with '%s'", "', '".join(names.keys()))

        return _try_action_until_timeout(
            "detect change",
            lambda: self._find_elements(names, return_change_type=return_change_type),
            timeout,
            catch=(WebDriverException,),
            rate=1,
        )

    def _do_while_element_exists(
        self, action_name: str, action: Action, element: ExpectElement = None
    ):
        """Executes an action as long as an element exists.
        Can be used to get rid of conditional elements.
        The action should remove the element.

        If no element is given the action is execution as long as it is successful
        (i.e. the element targeted by the action is still there)."""

        def __callback():
            try:
                if element:
                    # try to find the element
                    self._find_elements({"element to be removed": [element]})
                # try to remove the element using the action.
                # As soon as no error is raised from the action
                # the element is no longer there and we can abort (i.e. not raise an error).
                action.execute(self.driver)
            except (WebDriverException, ActionUnsuccessful):
                # if an exception was raise the element is not available (our goal)
                # and we can return (no error raised) which aborts the loop
                return

            # As long as calling action works the element is still there
            # and we have to try again. Raising an error continues the loop
            raise ActionUnsuccessful()

        _try_action_until_timeout(action_name, __callback, 60, (ActionUnsuccessful,), 1)

    def _transform_status_names(self, keys: list[str], format_values: dict[str, str] = None):
        """Creates a new dict with only the given keys, if they are in the original.
        Formats each value string of this the input dict with the values from the
        format_values dict, if given."""
        if format_values is None:
            return {k: self.status_change_names[k] for k in keys if k in self.status_change_names}

        result = {}
        for k in keys:
            if k in self.status_change_names:
                result[k] = []
                element: ExpectElement
                for element in self.status_change_names[k]:
                    element.value = element.value.format(**format_values)
                    result[k].append(element)
        return result

    def _text_on_screen(self, element: ExpectElement):
        """Uses OCR to detect text on screen. Requires Capabilities.DETECT_CHANGE_OCR."""
        raise NotImplementedError(
            "Use Capabilities.DETECT_CHANGE_OCR to enable OCR text detection."
        )

    def _pre_start_program(self):
        """Function that is called before _start_program"""

    def _start_program(self):
        """Starts the program without CLI arguments."""
        self.driver = RemoteDriver(
            command_executor="http://127.0.0.1:4723",
            desired_capabilities={"app": self.executable_path},
        )

    def _post_start_program(self):
        """Function that is called after _start_program"""

    def _pre_wait_program_load(self):
        """Function that is called before _wait_program_load"""

    def _wait_program_load(self, model: File, program_start_timeout: int):
        """Busy-wait for the program to load."""
        self._wait_for_change(
            names=self._transform_status_names(
                ["program loaded"],
                self._get_format_strings(model),
            ),
            timeout=program_start_timeout,
        )

    def _post_wait_program_load(self):
        """Function that is called after _wait_program_load"""

    def _pre_load_model(self):
        """Function that is called before _load_model"""

    @abstractmethod
    def _load_model(self, model: File):
        """Loads the model file in the program."""

    def _post_load_model(self):
        """Function that is called after _load_model"""

    def _pre_wait_model_load(self):
        """Function that is called before _wait_model_load"""

    def _wait_model_load(self, model: File, file_load_timeout: int):
        """Busy-wait for the model to load.
        ActionUnsuccessful is raised if the model cannot be loaded."""
        change_type = self._wait_for_change(
            names=self._transform_status_names(
                ["error", "file loaded"],
                self._get_format_strings(model),
            ),
            timeout=file_load_timeout,
        )
        if change_type == "error":
            raise ActionUnsuccessful("error msg detected in window")

    def _post_wait_model_load(self):
        """Function that is called after _wait_model_load"""

    def _post_model_load_failure(self):
        """Function that is called after the model failed to load."""

    def _post_model_load_success(self):
        """Function that is called after the model is successfully loaded."""

    def _pre_stop(self):
        """Function that is called before stop"""

    def stop(self) -> None:
        self.driver.quit()

    def force_stop_all(self) -> None:
        _stop_process(self.process_name)

    def _post_stop(self):
        """Function that is called after stop"""

    def _focus_window(self):
        """Focuses the current window, in case focus was lost."""
        self.driver.switch_to.window(self.driver.current_window_handle)

    def test(
        self,
        file: File,
        output_dir: str,
        program_start_timeout: int = 60,
        file_load_timeout: int = 30,
    ) -> Iterable[tuple[str, float, Iterable[DiskFile]]]:

        self.root = RemoteDriver(
            command_executor="http://127.0.0.1:4723",
            desired_capabilities={"app": "Root"},
        )

        self.force_stop_all()
        # sometimes stopping via PowerShell is too slow and
        # we connected to the already running instance, that is then closed.
        sleep(5)

        yield self.timestamp(State.PROGRAM_NOT_STARTED, output_dir, only_timestamp=True)

        try:
            self._pre_start_program()
            self._start_program()
            self._post_start_program()

            yield self.timestamp(State.PROGRAM_STARTED, output_dir, only_timestamp=True)
            self._focus_window()

            self._pre_wait_program_load()
            self._wait_program_load(file, program_start_timeout)
            self._post_wait_program_load()
        except (ActionUnsuccessful, WebDriverException) as err:
            logging.error("program not loaded, because: %s", err)
            yield self.timestamp(
                State.PROGRAM_NOT_LOADED, output_dir, only_timestamp=True, capture_exception=err
            )
            return
        except Exception as err:  # pylint:disable=broad-except
            logging.exception("program not loaded, due to unexpected error")
            yield self.timestamp(
                State.PROGRAM_NOT_LOADED, output_dir, only_timestamp=True, capture_exception=err
            )
            return
        else:
            yield self.timestamp(State.PROGRAM_LOADED, output_dir, only_timestamp=True)

        self._focus_window()
        self.driver.maximize_window()
        sleep(5)  # sometimes maximizing freezes the window, this makes sure its no problem

        yield self.timestamp(State.PROGRAM_PREPARED, output_dir)

        try:
            self._pre_load_model()
            self._load_model(model=file)
            self._post_load_model()

            self._focus_window()
            yield self.timestamp(State.MODEL_LOAD_STARTED, output_dir, only_timestamp=True)

            self._pre_wait_model_load()
            self._wait_model_load(file, file_load_timeout)
            self._post_wait_model_load()
        except (ActionUnsuccessful, WebDriverException) as err:
            logging.info("model not loaded, because: %s", err)
            yield self.timestamp(State.MODEL_NOT_LOADED, output_dir, capture_exception=err)
            self._post_model_load_failure()
        except Exception as err:  # pylint:disable=broad-except
            logging.exception("model not loaded, due to unexpected error")
            yield self.timestamp(
                State.MODEL_NOT_LOADED, output_dir, only_timestamp=True, capture_exception=err
            )
            self._post_model_load_failure()
        else:
            yield self.timestamp(State.MODEL_LOADED, output_dir)
            self._post_model_load_success()

        try:
            self._pre_stop()
            self.stop()
            self._post_stop()
        except (ActionUnsuccessful, WebDriverException) as err:
            logging.error("program could not be stopped: %s", err)
            self.force_stop_all()

        yield self.timestamp(State.PROGRAM_STOPPED, output_dir, only_timestamp=True)

        self.root.quit()

    def _take_screenshot(self) -> Union[bytes, Iterable[bytes]]:
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            yield self.driver.get_screenshot_as_png()

    def _take_snapshot(self) -> bytes:
        finished_proc = _run_ps_command(
            ["Get-Process", "-Name", self.process_name, "|", "ConvertTo-Json"]
        )
        return finished_proc.stdout


class AutomatedProgram(ABCMeta):
    """Metaclass (i.e. 'class factory') that creates an automated program class
    with the specified capabilities."""

    # pylint:disable=protected-access

    def __new__(
        cls,
        clsname,
        bases,
        attributes: dict[str, Any],
        capabilities: list[str] = None,
        additional_attributes: dict[str, Any] = None,
    ):
        def __require_attribute(capability: Capabilities, req_attributes: list[str]):
            """Raises an error if the defined attributes are not present."""
            for attribute in req_attributes:
                if attribute not in attributes:
                    raise ValueError(
                        f"attribute '{attribute}' is required for capability {capability}"
                    )

        if additional_attributes:
            attributes.update(additional_attributes)

        if capabilities is None:
            capabilities = []

        if Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE in capabilities:

            def _load_model(self, model: File):
                ActionChains(self.driver).send_keys(self.open_file_dialogue_keys).perform()
                sleep(2)
                self.driver.find_element_by_name("File name:").click()
                ActionChains(self.driver).send_keys(model.abspath).perform()
                ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()

            attributes["_load_model"] = _load_model

            __require_attribute(
                Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE, ["open_file_dialogue_keys"]
            )

        if (
            Capabilities.DETECT_CHANGE_SCREENSHOT in capabilities
            or Capabilities.DETECT_CHANGE_OCR in capabilities
        ):

            attributes["tempdir"] = tempfile.mkdtemp()
            logging.debug(
                "Use '%s' for temporary screenshots of '%s'", attributes["tempdir"], clsname
            )
            atexit.register(lambda: shutil.rmtree(attributes["tempdir"], ignore_errors=True))
            attributes["last_screenshot_path"] = str(
                Path(attributes["tempdir"], "last.png").resolve()
            )
            attributes["current_screenshot_path"] = str(
                Path(attributes["tempdir"], "current.png").resolve()
            )

        if Capabilities.DETECT_CHANGE_SCREENSHOT in capabilities:

            def _post_load_model(self):
                self.driver.save_screenshot(self.last_screenshot_path)
                sleep(2)

            def _screen_changed(self):
                """Checks if the screen updated."""
                self.driver.save_screenshot(self.current_screenshot_path)
                score = _compare_images(
                    _convert_image_to_ndarray(self.last_screenshot_path),
                    _convert_image_to_ndarray(self.current_screenshot_path),
                )
                shutil.copyfile(self.current_screenshot_path, self.last_screenshot_path)
                logging.debug("Screenshots compared to: %s", score)
                return score < 0.99999

            attributes["_post_load_model"] = _post_load_model
            attributes["_screen_changed"] = _screen_changed

        if Capabilities.DETECT_CHANGE_OCR in capabilities:

            def _text_on_screen(self, element: ExpectElement):
                """Checks if the specified text appears on the screenshot of the program."""
                for screenshot in self.screenshot():
                    with open(self.current_screenshot_path, "wb") as file:
                        file.write(screenshot)
                    img = Image.open(self.current_screenshot_path)
                    img = img.crop(element.ocr_bounding_box(*img.getbbox()))
                    img.save(self.current_screenshot_path)
                    detected_text = " ".join(
                        OCR_READER.readtext(self.current_screenshot_path, detail=0)
                    )
                    logging.debug("target text is: '%s'", element.value)
                    logging.debug("detected text is: '%s'", detected_text)
                    if element.value.lower() in detected_text.lower():
                        return True
                return False

            attributes["_text_on_screen"] = _text_on_screen

        if Capabilities.START_PROGRAM_LEGACY in capabilities:

            def _get_windows_by_title(self):
                """Based on: https://stackoverflow.com/a/3278356 (c) 2010 KobeJohn"""

                def _window_callback(hwnd, all_windows):
                    all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

                windows = []
                win32gui.EnumWindows(_window_callback, windows)
                handles = [
                    hwnd for hwnd, title in windows if self.window_title in title and hwnd != 0
                ]
                if handles:
                    return handles[0]
                raise ActionUnsuccessful(f"Could not find window with title {self.window_title}")

            def _start_program(self):
                _run_ps_command(["Start-Process", "-FilePath", f"'{self.executable_path}'"])
                window_handle = _try_action_until_timeout(
                    "wait for window",
                    self._get_windows_by_title,
                    timeout=30,
                    catch=(ActionUnsuccessful,),
                    rate=1,
                )
                if hasattr(self, "window_load_timeout"):
                    sleep(self.window_load_timeout)
                if "program starting" in self.status_change_names:
                    window_element: WebElement = self._wait_for_change(
                        names=self._transform_status_names(["program starting"]),
                        timeout=30,
                        return_change_type=False,
                    )
                    window_handle = window_element.get_attribute("NativeWindowHandle")
                self.driver = RemoteDriver(
                    command_executor="http://127.0.0.1:4723",
                    desired_capabilities={"appTopLevelWindow": f"0x{int(window_handle):X}"},
                )

            attributes["_get_windows_by_title"] = _get_windows_by_title
            attributes["_start_program"] = _start_program

            __require_attribute(Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE, ["window_title"])

        return super().__new__(cls, clsname, bases, attributes)
