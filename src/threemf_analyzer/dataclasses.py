"""Defines dataclasses for the run package."""

from dataclasses import dataclass
from os.path import join
from typing import Any


@dataclass
class DiskFile:
    """Class that holds the information about a file that is to be stored on disk.

    Attributes:
        stem (str): Name without file extension.
        extension (str): File extension.
        abspath (str): The absolute path to the directory the file should be stored in.
    """

    stem: str
    extension: str
    abspath: str
    content: Any = None

    def write(self):
        """Write the content of this object to disk."""
        path = join(self.abspath, f"{self.stem}.{self.extension}")
        if isinstance(self.content, bytes):
            with open(path, "wb") as file:
                file.write(self.content)
        else:
            with open(path, "w", encoding="utf-8") as file:
                file.write(self.content)


@dataclass(eq=True, frozen=True, order=True)
class File:
    """Class that holds the information about a file.

    Attributes:
        stem (str): Name without file extension.
        name (str): Name with file extension.
        abspath (str): The absolute path to the file.
        test_id (str): ID of the test that this file belongs to (name/stem starts with this).
    """

    stem: str
    name: str
    abspath: str
    test_id: str

    def __repr__(self) -> str:
        return self.test_id
