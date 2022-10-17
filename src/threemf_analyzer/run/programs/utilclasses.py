"""Small classes that hold information."""
from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from appium.webdriver import Remote as RemoteDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By as _By


class By(_By):
    """Extended version of the By class from selenium."""

    AUTOMATION_ID = "accessibility id"
    OCR = "ocr"


class ActionUnsuccessful(Exception):
    """Raised if an action (on a program) was not successful"""


class Be(Enum):
    """State of an element to select."""

    NOTAVAILABLE = "not available"
    AVAILABLE = "available"
    AVAILABLE_NOTENABLED = "available and not enabled"
    AVAILABLE_ENABLED = "available and enabled"


class Context(Enum):
    """WinAppDriver session to use, where
    ROOT is the global session and
    SELF is the specific session for this program."""

    ROOT = "ROOT"
    SELF = "SELF"


@dataclass
class ExpectElement:
    """
    Holds the values with which we can check whether the element is there or not.

    by: the type of property we check by
    value: the string value we check the property against to identify the element
    expect: the state we expect the element to be in
    parents: a list of elements that are parent to this element
        (might be needed to find the element)
        Parents overwrite the context (i.e. the context of the first parent is the
        only one used.)
    context: WinAppDriver session that is used to find the element
    """

    by: By
    value: str
    expect: Be = Be.AVAILABLE
    parents: list["ExpectElement"] = field(default_factory=lambda: [])
    context: Context = Context.SELF


class Capabilities(Enum):
    """Capabilities a program class can have when using the metaclass."""

    OPEN_MODEL_VIA_FILE_DIALOGUE = "OPEN_MODEL_VIA_FILE_DIALOGUE"
    DETECT_CHANGE_SCREENSHOT = "DETECT_CHANGE_SCREENSHOT"
    DETECT_CHANGE_OCR = "DETECT_CHANGE_OCR"
    START_PROGRAM_LEGACY = "START_PROGRAM_LEGACY"


class State:
    """State of the program. Used for timestamps."""

    PROGRAM_NOT_STARTED = "00 program-not-started"
    PROGRAM_STARTED = "01 program-started"
    PROGRAM_NOT_LOADED = "02 program-not-loaded"
    PROGRAM_LOADED = "02 program-loaded"
    PROGRAM_PREPARED = "03 program-prepared"
    MODEL_LOAD_STARTED = "04 model-started-loading"
    MODEL_NOT_LOADED = "05 model-not-loaded"
    MODEL_LOADED = "05 model-loaded"
    PROGRAM_STOPPED = "06 program-stopped"


@dataclass
class Action:
    """An action to be executed later."""

    value: Any

    @abstractmethod
    def execute(self, driver: RemoteDriver):
        """Executes the action using the given driver.
        Might utilize the value."""


class Click(Action):
    """value is the ExpectElement to click on, can be None"""

    def execute(self, driver: RemoteDriver):
        self.value: ExpectElement
        try:
            driver.find_element(self.value.by, self.value.value).click()
        except Exception as err:
            raise ActionUnsuccessful(f"Cannot click on {self.value}") from err


class PressKeys(Action):
    """value is the keys string to press"""

    def execute(self, driver: RemoteDriver):
        self.value: str
        try:
            ActionChains(driver).send_keys(self.value).perform()
        except Exception as err:
            raise ActionUnsuccessful(f"Cannot click on {self.value}") from err


class ChangeType:
    """Defines state names that can be detected using ExpectElements."""

    PROGRAM_LOADED = "program loaded"
    MODEL_LOADED = "file loaded"
    MODEL_LOADING = "file loading"
    INTERACTIVE_ELEMENT_APPEARED = "question asked"
    ERROR_DETECTED = "error"
    DETECT_ROOT_WINDOW_only_legacy_start_mode = "program starting"
