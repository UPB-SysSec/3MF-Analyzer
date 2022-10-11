"""Small classes that hold information."""

from dataclasses import dataclass, field
from enum import Enum

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
