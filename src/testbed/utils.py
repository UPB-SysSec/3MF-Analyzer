"""Differrent utility functions."""

import fnmatch
import logging
import os
import queue
import threading
from functools import lru_cache
from glob import glob
from os.path import join
from typing import Any, Dict, Generator, List

from . import yaml
from .dataclasses import File, Program

logging.getLogger("xmlschema").setLevel(logging.WARNING)

import xmlschema
from xmlschema.etree import ParseError

from . import BUILD_DIR, DESCRIPTION_DIR, DESCRIPTION_GLOB, PROGRAMS_DIR, XSD_FILES


def pprint_information(infos: Dict[str, str]) -> None:
    """Pretty prints all the information given in the dict about a testcase."""

    print(
        "-" * 80,
        f'{infos.get("destination_path")}',
        "",
        infos.get("description"),
        "",
        infos.get("content"),
        sep="\n",
        end="\n\n",
    )


def validate_tmf_model_xml(xml: str, specification_id: str) -> Dict[str, str]:
    """Validates the given XML string (or path to file) against all 3MF XSD Schemas.
    Returns a dict that tells you for each schema if the XML is valid, or not."""
    from .create.tmf_model_mutator.base_models import INITIAL_MODELS

    target_spec_names = ["core", INITIAL_MODELS.get(specification_id, {}).get("specification", "")]
    target_specs = {name: XSD_FILES[name] for name in target_spec_names if name in XSD_FILES}
    res = {}

    for name, path in target_specs.items():
        try:
            xmlschema.validate(xml_document=xml, schema=path)
            res[name] = "Valid"
        except xmlschema.XMLSchemaValidationError as err:
            res[name] = f"Invalid 3MF: {err.reason}"
        except xmlschema.XMLSchemaValidatorError as err:
            # more general than last case, not sure if it can happen
            res[name] = f"Invalid 3MF: {err.message}"
        except xmlschema.XMLSchemaException:
            # most general error validate raises, not sure if it can happen
            res[name] = "Invalid 3MF"
        except ParseError:
            res[name] = "Invalid XML"

    return res


def multithread_generators(
    generators: List[Generator[Any, Any, Any]], keep_order: bool = True
) -> Generator[Any, Any, Any]:
    """Takes a list of generators, executes them in parallel, and yields the results.
    If keep_order is True the results are cached (might be extremely memory hungry,
    depending on the size of the generator), else the first results to come in are yielded.
    If generator yield None values, those are ignored."""

    def worker(generator: Generator[Any, Any, Any], result_queue: queue.Queue) -> None:
        """Runs the generator and puts the results in a queue.
        Ends the queue with None. If any value in between in None, skip it."""
        for item in generator:
            if item is not None:
                result_queue.put(item)
        result_queue.put(None)

    if keep_order:
        result_queues = [queue.Queue() for _ in generators]
        for generator, result_queue in zip(generators, result_queues):
            threading.Thread(
                target=worker,
                args=(generator, result_queue),
                daemon=True,
            ).start()
        for result_queue in result_queues:
            while True:
                res = result_queue.get()
                if res is None:
                    break
                yield res
    else:
        results_queue = queue.Queue()
        for generator in generators:
            threading.Thread(
                target=worker,
                args=(generator, results_queue),
                daemon=True,
            ).start()
        nr_finished_generators = 0
        while nr_finished_generators < len(generators):
            res = results_queue.get()
            if res is None:
                nr_finished_generators += 1
            else:
                yield res


def get_worker(func):
    """Creates a thread worker from a function.
    Calls the function indefinitely on the given queue,
    unpacks the queue items directly as args for the function."""

    def worker(input_queue: queue.Queue):
        while True:
            args = input_queue.get()
            func(*args)
            input_queue.task_done()

    return worker


def get_all_tests() -> Dict[str, Dict]:
    """Returns a dict with all tests in it."""
    all_tests = {}
    for file_path in glob(DESCRIPTION_GLOB):
        with open(file_path, "r", encoding="utf-8") as desc_file:
            content = yaml.load(desc_file)
            all_tests.update(content.get("tests", {}))

    return all_tests


@lru_cache
def _get_all_tests_by_type():
    description_files = sorted(glob(DESCRIPTION_GLOB))
    with open(join(DESCRIPTION_DIR, "description_texts.yaml"), "r", encoding="utf-8") as in_file:
        description_texts = yaml.load(in_file)

    types = description_texts["types"]
    footnotes = {}

    for file_path in description_files:
        # Sorts the tests descripted in the yaml (that belongs to the path) into the types obj.
        # Does the same with footnotes

        with open(file_path, "r", encoding="utf8") as yaml_file:
            content = yaml.load(yaml_file)

        for key, text in content.get("footnotes", {}).items():
            footnotes[key] = text

        scope = content.get("scope", "")

        def _get_type_entry(type_str: str):
            if type_str is None:
                return
            current_root = {"subtypes": types}
            for sub_type in type_str.split(","):
                sub_type = sub_type.strip()
                new_root = current_root.get("subtypes", {}).get(sub_type)
                if new_root is None:
                    return
                current_root = new_root
            return current_root

        for test_id, infos in content.get("tests", {}).items():
            target_type = _get_type_entry(infos.get("type"))
            if target_type is None:
                target_type = types["Miscellaneous"]
            infos["scope"] = scope
            if "tests" not in target_type:
                target_type["tests"] = {}
            target_type["tests"][test_id] = infos

    return types, footnotes


def get_all_tests_by_type(get_footnotes: bool = False, callback=None):
    """Returns a dict with all tests in it, sorted by type.
    If get_footnotes is set, returns tuple.
    If callback is given, the function is called on every nested type with the kwargs:
    nesting_level, type_name, type_description, contained_tests
    An array of callback results is returned"""

    types, footnotes = _get_all_tests_by_type()

    if get_footnotes:
        return types, footnotes
    if callback is not None:

        def _types_to_sections(types: Dict, section_level: int = 0) -> List:
            res = []
            for type_name, infos in types.items():
                res.append(
                    callback(
                        nesting_level=section_level,
                        type_name=type_name,
                        type_description=infos.get("description", ""),
                        contained_tests=infos.get("tests", {}),
                    )
                )
                if "subtypes" in infos:
                    res += _types_to_sections(infos["subtypes"], section_level=section_level + 1)
            return res

        return _types_to_sections(types)

    return types


def parse_programs(program_ids: str) -> List[Program]:
    """Parses given strings into Program objects if possible. Ignores non-existing IDs."""
    programs = []
    with open(join(PROGRAMS_DIR, "config.yaml"), "r", encoding="utf-8") as in_file:
        for program in yaml.load(in_file):
            try:
                if program["id"] in program_ids.split(",") or program_ids == "ALL":
                    if not program.get("window_title"):
                        program["window_title"] = program["name"]
                    if not program.get("type_association_id"):
                        program["type_association_id"] = None
                    if not program.get("exec_path"):
                        program["exec_path"] = None
                    programs.append(Program(**program))
            except (KeyError, TypeError) as err:
                logging.error(err)

    logging.info("Target programs: %s", programs)
    assert len(programs) > 0, "No matching programs found"
    return programs


def parse_tests(test_ids: str) -> List[File]:
    """Parses given strings into File objects if possible. Ignores non-existing IDs."""
    existing_filenames = []
    for dirpath, _, filenames in os.walk(BUILD_DIR):
        existing_filenames += [(filename, join(dirpath, filename)) for filename in filenames]

    all_tests = get_all_tests()

    def _add_file(_test_id: str, _files: set):
        filename = None
        filepath = None
        possible_paths = [
            (name, path)
            for name, path in existing_filenames
            if name.lower().startswith(_test_id.lower())
        ]

        if len(possible_paths) == 1:
            filename, filepath = possible_paths[0]
        if len(possible_paths) > 1:
            for name, path in possible_paths:
                if f"{_test_id}.3mf" == name:
                    filename, filepath = name, path
                    break
        logging.debug("Use file %s for testcase %s", filename, _test_id)

        if _test_id in all_tests:
            if filename and filepath:
                _files.add(
                    File(
                        stem=filename.split(".")[0],
                        name=filename,
                        abspath=filepath,
                        test_id=_test_id,
                    )
                )
            else:
                logging.warning(
                    "Did not add test case %s, because the file does not exist in the build folder",
                    _test_id,
                )
        else:
            logging.warning(
                "Did not add test case %s, because it is not defined in a description YAML",
                _test_id,
            )

    files = set()
    if test_ids == "ALL":
        for test_id in all_tests:
            _add_file(test_id, files)
    elif test_ids.startswith("type:"):
        for full_test_id, test_info in all_tests.items():
            if test_info.get("type", "").startswith(test_ids[5:]):
                _add_file(full_test_id, files)
    else:
        for test_id in test_ids.split(","):
            test_id = test_id.strip()
            for matched_id in fnmatch.filter(all_tests.keys(), test_id):
                _add_file(matched_id, files)

    files = sorted(list(files))
    logging.info("Target files: %s", files)
    assert len(files) > 0, "No matching test files found"
    return files
