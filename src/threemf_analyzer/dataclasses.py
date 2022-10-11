"""Defines dataclasses for the run package."""

from dataclasses import dataclass
from os.path import join
from typing import Any


@dataclass(eq=True, frozen=True, order=True)
class Program:
    """Class that holds the information about a program from `config.yaml`.

    Attributes:
        id (str): The internal ID for a program, is also used as file/folder name where appropriate.
        name (str): Printable name of the program.
        type_association_id (str): The ID given by Windows, this is used in the SFTA script.
            The ID can be found by the Get-FTA function from the SFTA script as well.
        exec_path (str): Path to the executable (.exe) to be executed directly instead of through
            type associations.
        process_name (str): The name of the process when running.
            Among others, used to kill the program.
        window_title (str): Format string version of the window's title.
            This is used to identify the window to optain a screenshot.
            The string has to occur in the window's title and should be as exact as possible,
            as not to select another window.
            If not explicitly given is the same as the name.
            Supported format string variables are:
            - filename: Name of the currently processed file
            - filename_ext: Name of the currently processed file with extension
            - program_name: name variable of this object
            - process_name: process_name variable of this object
    """

    id: str
    name: str
    type_association_id: str
    exec_path: str
    process_name: str
    window_title: str

    def __repr__(self) -> str:
        return self.id


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
