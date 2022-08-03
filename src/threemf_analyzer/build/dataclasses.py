"""Defines dataclasses for the run package."""

from dataclasses import dataclass


@dataclass
class Folder:
    """Simple namespace class for information about folders.

    All paths are absolute.

    Attributes:
        filetype (str): identifies if this hook should be active
        src_path (str): represents the path to the source folder
        foldername (str): foldername without extension
        dst_path (str): the directory where the resulting file should be stored
    """

    filetype: str
    src_path: str
    foldername: str
    dst_path: str
