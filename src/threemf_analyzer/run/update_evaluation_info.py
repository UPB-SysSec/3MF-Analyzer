import os
from glob import glob
from os.path import isdir, isfile, join
from textwrap import dedent
from typing import Any

from .. import DESCRIPTION_GLOB, EVALUATION_DIR, yaml


def _modify_eval_info(
    folder_path: str,
    verification_results: dict = None,
    program_infos: dict = None,
):
    """Calls all functions that modify the `info.yaml` file."""

    def _add_new_tests(content: dict) -> dict:
        """Add dummy entries for new IDs in the described tests."""

        ids = []

        description_files = sorted(glob(DESCRIPTION_GLOB))
        for file_path in description_files:
            with open(file_path, "r", encoding="utf8") as file:
                descriptions = yaml.load(file)
                ids += descriptions.get("tests", {}).keys()

        new_tests = {}
        for _id in ids:
            if _id in content["tests"]:
                new_tests[_id] = content["tests"][_id]
            else:
                new_tests[_id] = {"info": "TODO"}

        if "deprecated" not in content:
            content["deprecated"] = {}

        for _id, data in content["tests"].items():
            if _id not in new_tests:
                content["deprecated"][_id] = data

        content["tests"] = new_tests

        return content

    def _add_verification_results(content: dict, verification_results: dict) -> dict:
        for _id, data in verification_results.items():
            if _id not in content["tests"]:
                content["tests"][_id] = {}
            for key in [
                "missing_process_info",
                "missing_screenshot",
                "critical",
                "has_server_log",
                "server_log_interesting",
                "problems",
            ]:
                if key in content["tests"][_id]:
                    del content["tests"][_id][key]
            for key, val in data.items():
                content["tests"][_id][key] = val
        return content

    def _add_program_infos(content: dict, program_infos: dict) -> dict:
        if program_infos["product"]:
            content["name"] = program_infos["product"]
        if program_infos["company"]:
            content["company"] = program_infos["company"]
        if program_infos["version"]:
            content["version"] = program_infos["version"].replace(" ", "")
        return content

    with open(join(folder_path, "info.yaml"), "r", encoding="utf8") as yaml_file:
        content = yaml.load(yaml_file)

    content = _add_new_tests(content)
    if verification_results:
        content = _add_verification_results(content, verification_results)
    if program_infos:
        content = _add_program_infos(content, program_infos)

    with open(join(folder_path, "info.yaml"), "w", encoding="utf8") as yaml_file:
        yaml.dump(content, yaml_file)


def modify_all_eval_info(
    verification_results: dict[str, dict[str, dict[str, Any]]] = None,
    programs_infos: dict[str, dict[str, str]] = None,
):
    """Updates the evaluation info.yaml and the description yaml files with new data.
    programs is only needed if program_infos is also given."""
    base_dir = join(EVALUATION_DIR)

    for entry in os.listdir(base_dir):
        folder = join(base_dir, entry)
        if isdir(folder):
            if not isfile(join(folder, "info.yaml")):
                with open(join(folder, "info.yaml"), "w", encoding="utf-8") as yaml_file:
                    stem = f"""\
                        name: {entry}
                        company: ""
                        version: ""

                        tests: {{}}
                        """
                    yaml_file.write(dedent(stem))
            program_infos = None
            if programs_infos is not None:
                program_infos = programs_infos.get(entry)
            if verification_results:
                _modify_eval_info(
                    folder,
                    verification_results=verification_results.get(entry),
                    program_infos=program_infos,
                )
            else:
                _modify_eval_info(
                    folder,
                    program_infos=program_infos,
                )
