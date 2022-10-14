"""Creates testcases based on XML attacks."""
from copy import deepcopy
from os.path import join
from textwrap import dedent
from typing import Generator

from ... import STATIC_FILE_DIR_SRC, TESTFILE_GENERATED_SRC_DIR
from ..tmf_model_mutator.base import ComplexType
from .base_objects import BASE_MODEL, BASE_MODEL_DTD, BASE_RELATIONSHIP, BASE_RELATIONSHIP_DTD
from .server_files import SERVER_FILES
from .test_cases import TESTCASES


def create_xml_testcases() -> Generator[dict[str, str], None, None]:
    """Creates the defined test files."""

    def _create_xml_testcases(
        base_element: ComplexType,
        dtd: str,
        folder_name: str,
        id_prefix: str,
        manipulation_property: str,
        file_suffix: str,
        description_addon: str,
    ):
        destination_folder = join(TESTFILE_GENERATED_SRC_DIR, folder_name)
        code_format_paramters = {
            "ROOT": base_element.tag,
            "DTD": dtd,
        }
        for testcase in TESTCASES:
            if testcase.get(manipulation_property) is None:
                continue
            xml = '<?xml version="1.0" encoding="utf-8"?>\n'
            xml += "\n"
            xml += dedent(testcase.get("prefixed_code", "")).format(**code_format_paramters) + "\n"
            xml += "\n"
            base = deepcopy(base_element)
            for function in testcase.get(manipulation_property, []):
                base = function(base)
            xml += base.to_xml()
            xml += "\n"
            xml += dedent(testcase.get("postfixed_code", "")).format(**code_format_paramters) + "\n"

            while "\n\n\n" in xml:
                xml = xml.replace("\n\n\n", "\n\n")

            yield {
                "id": id_prefix + testcase["id"],
                "description": f'{testcase.get("name", "")} {description_addon}'
                + str(". " + testcase["description"] if "description" in testcase else ""),
                "content": xml,
                "destination_path": join(
                    destination_folder, id_prefix + testcase["id"] + file_suffix
                ),
                "is_valid": {"core": "Invalid XML"},
                "type": testcase["type"],
            }

    yield from _create_xml_testcases(
        BASE_MODEL,
        BASE_MODEL_DTD,
        "xml.3mf_models",
        "XML-MOD-",
        "model_manipulation",
        ".model",
        "(in .model file)",
    )
    yield from _create_xml_testcases(
        BASE_MODEL,
        BASE_MODEL_DTD,
        "xml.3mf_models",
        "XML-MOD-ALT-",
        "model_alt_manipulation",
        ".model",
        "(in .model file; alternative)",
    )
    yield from _create_xml_testcases(
        BASE_RELATIONSHIP,
        BASE_RELATIONSHIP_DTD,
        "xml.3mf_rels",
        "XML-REL-",
        "rels_manipulation",
        ".rels",
        "(in .rels file)",
    )


def get_server_files() -> Generator[dict[str, str], None, None]:
    """Yields the different server files."""
    for file in SERVER_FILES:
        yield {
            "content": dedent(file["content"]),
            "destination_path": join(STATIC_FILE_DIR_SRC, file["name"]),
        }
