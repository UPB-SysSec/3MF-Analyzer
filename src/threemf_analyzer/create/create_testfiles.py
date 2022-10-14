"""Writes the generated testcases to disc and adds an entry in the correct YAML file for them."""

import itertools
import logging
from os.path import dirname, isfile, join
from pathlib import Path
from textwrap import dedent

from .. import DESCRIPTION_DIR, yaml
from .opc_test_creator import create_opc_testcases
from .tmf_model_mutator import mutate_tmf_models
from .xml_test_creator import create_xml_testcases, get_server_files


def _create_file(path: str, content: str) -> None:
    logging.info("Create file %s", path)
    Path(dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as out_file:
        out_file.write(content)


def _unify_str(string: str):
    """Creates comparable version of a string."""
    string = " ".join(string.split(" "))
    string = string.replace("\n", " ")
    return string.strip()


def _create_testcase_entry(
    test_id: str,
    description: str,
    test_content: dict,
    is_valid: dict[str, str] = None,
    expected_behavior: str = None,
    type_str: str = None,
) -> None:
    logging.info("Update YAML entry of %s", test_id)

    if name := description.split(". ")[0].strip():
        test_content["name"] = name
    test_content["created"] = True
    if is_valid is not None:
        test_content["conforms_to_spec"] = test_content.get("conforms_to_spec", {})
        for spec, value in is_valid.items():
            test_content["conforms_to_spec"][spec] = value

    if expected_behavior is not None:
        test_content["expected_behavior"] = expected_behavior

    if test_id.startswith("XML-"):
        if not test_content.get("expected_behavior"):
            test_content["expected_behavior"] = "Ignore DTD or Fail"

    if type_str is not None:
        test_content["type"] = type_str

    if further_infos := ".".join(description.split(". ")[1:]).strip():
        _orig = test_content.get("further_infos", "")
        if _orig:
            if _unify_str(further_infos) not in _unify_str(_orig):
                _orig += "\n" + further_infos
        else:
            _orig = further_infos
        test_content["further_infos"] = _orig


def _remove_old_entries(all_ids: list[str]):
    """Removes all entries that are not in the given list."""
    mappings = {
        "XML": {
            "filename": "02_xml.yaml",
            "ids": [],
        },
        "GEN": {
            "filename": "03_3mf-mutated.yaml",
            "ids": [],
        },
    }
    for category, info in mappings.items():
        relevant_ids = [test_id for test_id in all_ids if test_id.startswith(category)]
        if not relevant_ids:
            continue
        path = join(DESCRIPTION_DIR, info["filename"])

        with open(path, "r", encoding="utf8") as yaml_file:
            content = yaml.load(yaml_file)

        obsolete_ids = [test_id for test_id in content["tests"] if test_id not in relevant_ids]

        content["tests"] = {
            test_id: content["tests"][test_id]
            for test_id in sorted(content["tests"].keys())
            if test_id not in obsolete_ids
        }

        with open(path, "w", encoding="utf8") as yaml_file:
            yaml.dump(content, yaml_file)


def create_testfiles(parsed_arguments: dict[str, str]) -> None:
    """Writes the generated testcases to disc and adds an entry in the correct YAML file for them."""

    _generators = [get_server_files()]
    if not parsed_arguments.get("disable_xml_based"):
        _generators += [create_xml_testcases()]
    if not parsed_arguments.get("disable_3mf_based"):
        _generators += [mutate_tmf_models()]
    if not parsed_arguments.get("disable_opc_based"):
        _generators += [create_opc_testcases()]

    # make sure files exists and read their content from yaml
    file_contents = {}
    for filename in ["02_xml.yaml", "03_3mf-mutated.yaml", "00_3mf.yaml", "04_opc.yaml"]:
        path = join(DESCRIPTION_DIR, filename)
        if not isfile(path):
            with open(path, "w", encoding="utf-8") as yaml_file:
                stem = """\
                    scope: TODO

                    tests: {{}}
                    """
                yaml_file.write(dedent(stem))

        with open(path, "r", encoding="utf8") as yaml_file:
            file_contents[filename] = yaml.load(yaml_file)

    all_ids = []
    for obj in itertools.chain(*_generators):
        _create_file(obj["destination_path"], obj["content"])
        if "id" in obj:
            if obj["id"].startswith("XML-"):
                content = file_contents["02_xml.yaml"]
            elif obj["id"].startswith("GEN-"):
                content = file_contents["03_3mf-mutated.yaml"]
            elif obj["id"].startswith("R-"):
                content = file_contents["00_3mf.yaml"]
            elif obj["id"].startswith("CS-"):
                content = file_contents["04_opc.yaml"]

            if obj["id"] not in content["tests"]:
                content["tests"][obj["id"]] = {}
            _create_testcase_entry(
                obj["id"],
                obj["description"],
                content["tests"][obj["id"]],
                is_valid=obj.get("is_valid"),
                expected_behavior=obj.get("expected_behavior"),
                type_str=obj.get("type"),
            )
            all_ids.append(obj["id"])

    for filename in ["02_xml.yaml", "03_3mf-mutated.yaml", "00_3mf.yaml", "04_opc.yaml"]:
        path = join(DESCRIPTION_DIR, filename)
        with open(path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(file_contents[filename], yaml_file)
    _remove_old_entries(all_ids)
