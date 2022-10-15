"""Base classes for programs."""

import json
import logging
from abc import ABC, abstractmethod
from copy import copy
from pathlib import Path
from time import time
from typing import Iterable, Union

from ...dataclasses import DiskFile, File
from .utilclasses import ActionUnsuccessful
from .utils import _try_action_until_timeout


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

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{type(self)}({self.name})"

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
        Return value is a generator of timestamps.
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
        file (you still need to call .write on the DiskFile),
        or (if not DiskFile was provided) returns the bytes of the screenshot that
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
            yield from screenshots

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

    def timestamp(
        self,
        name: str,
        output_directory: str,
        only_timestamp: bool = False,
        take_screenshot: bool = True,
        take_snapshot: bool = True,
    ) -> tuple[str, float]:
        """Takes a screenshot and snapshot,
        returns the data with the time it was taken and the given name."""

        if only_timestamp:
            take_screenshot = False
            take_snapshot = False

        data = {"timestamp": time()}

        if take_screenshot:
            data["screenshot"] = True
            try:
                screenshots = list(
                    self.screenshot(
                        write_to=DiskFile(
                            stem=f"screenshot_{name.replace(' ','_')}",
                            extension="png",
                            abspath=output_directory,
                        )
                    )
                )
                for screenshot in screenshots:
                    screenshot.write()
            except ActionUnsuccessful as err:
                logging.error(
                    "Tried to take screenshot for timestamp '%s', but failed with '%s'", name, err
                )
                data["screenshot_error"] = str(err)

        if take_snapshot:
            data["snapshot"] = True
            try:
                self.snapshot(str(Path(output_directory, f"snapshot_{name.replace(' ','_')}")))
            except ActionUnsuccessful as err:
                logging.error(
                    "Tried to take snapshot for timestamp '%s', but failed with '%s'", name, err
                )
                data["snapshot_error"] = str(err)

        return (name, data)
