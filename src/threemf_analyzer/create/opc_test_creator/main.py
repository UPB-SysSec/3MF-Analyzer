"""Creates testcases based on XML attacks."""
import itertools
from os.path import join
from textwrap import dedent
from typing import Generator

from ... import TESTFILE_GENERATED_SRC_DIR
from .lfi_testcases import create_lfi_testcases
from .reference_testcases import create_opc_reference_testcases


def create_opc_testcases() -> Generator[dict[str, str], None, None]:
    """Creates the defined test files."""

    testcase: dict
    for testcase in itertools.chain(create_opc_reference_testcases(), create_lfi_testcases()):
        # each test case creates one folder
        # we thus yield the dict with the ID once, and all other files as simple files
        id_dict_yeilded = False
        for filename, content in testcase["files"].items():
            if not id_dict_yeilded:
                id_dict_yeilded = True
                yield {
                    "id": testcase["id"],
                    "description": testcase["description"],
                    "content": dedent(content),
                    "destination_path": join(
                        TESTFILE_GENERATED_SRC_DIR, testcase["relative_folder"], filename
                    ),
                    "is_valid": {"core": testcase["is_valid"]},
                    "type": testcase["type"],
                }
                continue

            yield {
                "content": dedent(content),
                "destination_path": join(
                    TESTFILE_GENERATED_SRC_DIR, testcase["relative_folder"], filename
                ),
            }
