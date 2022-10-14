"""Verify the execution results and report failed executions."""

# pylint: disable=bare-except

import json
import logging
from copy import copy
from glob import glob
from os.path import getsize, isfile, join

from PIL import Image

from .. import EVALUATION_DIR, yaml
from ..dataclasses import File, Program
from ..utils import get_all_tests


def _empty_file(file_path) -> bool:
    """Tests if file at file_path is empty"""
    try:
        return getsize(file_path) == 0
    except OSError:
        return True


def _empty_json(file_path) -> bool:
    """Tests if file at file_path is empty json"""
    if not _empty_file(file_path):
        with open(file_path, "rb") as in_file:
            content = json.loads(in_file.read().decode("utf-8", "ignore"))
        if isinstance(content, list) or isinstance(content, dict):
            return not content
    return True


def _empty_screenshot(file_path) -> bool:
    """Tests if picture at file_path is empty. Empty means one of the following:
    - literally no content
    - very little different colors (basically mono-color)
    - very small in both width and height (both <500px)
    """
    if not _empty_file(file_path):
        try:
            img = Image.open(file_path).convert("L")
        except:
            return True
        darkest, lightest = img.getextrema()
        if darkest + 25 > lightest:
            # no real color difference in picture
            # probability hight, that broken
            return True
        width, height = img.size
        if width < 100 and height < 100:
            # if the screenshot is smaller something is broken
            # not even error popups should be this small in both dimensions
            # craftware, e.g., puts the error popup as the main window (and in foreground)
            # so a screenshot only captures the popup. that should not make it invalid.s
            return True
        return False
    return True


def _trivial_server_log(file_path) -> bool:
    """Tests if a server with more than the test-request exists"""
    if not _empty_file(file_path):
        with open(file_path, "r", encoding="utf-8") as in_file:
            content = in_file.read()
            for line in content.split("\n"):
                if len(line.strip()) > 0 and r"/Start%20server%20log" not in line:
                    return False
    return True


def _verify_lib3mf(program: Program, files: list[File], results: dict, rerun_tests: dict):
    for file in files:
        output_dir = join(EVALUATION_DIR, program.id, "snapshots", file.test_id)
        if isfile(join(output_dir, "error-info.txt")):
            with open(join(output_dir, "error-info.txt"), "r", encoding="utf-8") as err_file:
                results[program.id][file.test_id] = {
                    "critical": True,
                    "problems": [err_file.read()],
                }
                rerun_tests.append(file.test_id)
                continue

        res = {
            "problems": [],
        }

        if len(glob(join(output_dir, "*.png"))) == 0:
            res["critical"] = True
            res["problems"].append("No rendered model.")
            rerun_tests.append(file.test_id)

        # check server log
        serverlog_file_path = join(output_dir, "local-server.log")
        res["has_server_log"] = not _empty_file(serverlog_file_path)
        res["server_log_interesting"] = not _trivial_server_log(serverlog_file_path)

        # remove superfluous information (not there == falsy)
        for key, value in copy(res).items():
            if not value:
                del res[key]

        results[program.id][file.test_id] = res


def _verify_graphical_programs(
    program: Program, files: list[File], results: dict, rerun_tests: dict
):
    for file in files:
        output_dir = join(EVALUATION_DIR, program.id, "snapshots", file.test_id)
        try:
            with open(join(output_dir, "snapshot_intervals.txt"), "r", encoding="utf-8") as infile:
                snapshot_intervals = [int(ival) for ival in infile.read().split(",")]
        except OSError:
            logging.warning(
                "%s with %s has not snapshot_interval.txt file. Aborting.",
                program.id,
                file.test_id,
            )
            rerun_tests.append(file.test_id)
            continue

        if isfile(join(output_dir, "error-info.txt")):
            with open(join(output_dir, "error-info.txt"), "r", encoding="utf-8") as err_file:
                results[program.id][file.test_id] = {
                    "critical": True,
                    "problems": [err_file.read()],
                }
                rerun_tests.append(file.test_id)
                continue

        res = {
            "missing_process_info": 0,
            "missing_screenshot": 0,
            "problems": [],
        }

        interval_filenames = [
            f"{number+1:02}_{timeinterval}s-after-start"
            for number, timeinterval in enumerate(snapshot_intervals)
        ]

        # check generated JSON process information
        if len(glob(join(output_dir, "*.json"))) == 0:
            res["critical"] = True
            res["problems"].append("No process information files.")
            del res["missing_process_info"]
        else:
            for filename in ["00_at-init"] + interval_filenames:
                if _empty_json(join(output_dir, filename + ".json")):
                    logging.info(
                        "%s with %s is missing %s.json", program.name, file.test_id, filename
                    )
                    res["missing_process_info"] += 1
            if res["missing_process_info"] >= len(["00_at-init"] + interval_filenames) - 1:
                res["critical"] = True
                res["problems"].append("Too many missing process information files.")

        # check generated screenshots
        if len(glob(join(output_dir, "*.png"))) == 0:
            res["critical"] = True
            res["problems"].append("No screenshot files.")
            del res["missing_screenshot"]
        else:
            for filename in interval_filenames:
                if _empty_screenshot(join(output_dir, filename + ".png")):
                    logging.info(
                        "%s with %s is missing %s.png", program.name, file.test_id, filename
                    )
                    res["missing_screenshot"] += 1
            if res["missing_screenshot"] >= len(interval_filenames) - 1:
                res["critical"] = True
                res["problems"].append("Too many missing/broken screenshot files.")

        if res.get("critical"):
            rerun_tests.append(file.test_id)

        # check server log
        serverlog_file_path = join(output_dir, "local-server.log")
        res["has_server_log"] = not _empty_file(serverlog_file_path)
        res["server_log_interesting"] = not _trivial_server_log(serverlog_file_path)

        # remove superfluous information (not there == falsy)
        for key, value in copy(res).items():
            if not value:
                del res[key]

        # set result to actual object
        results[program.id][file.test_id] = res


def verify_results(
    programs: list[Program], files: list[File]
) -> dict[str, dict[str, dict[str, Any]]]:
    """Ensures that all tests run successfully, if not return arguments to re-run them."""

    results = {}
    rerun_flags = []
    all_test_ids = get_all_tests().keys()

    for program in programs:
        results[program.id] = {}  # remember tests for this program to redo
        rerun_tests = []

        if program.id == "lib3mf":
            _verify_lib3mf(program, files, results, rerun_tests)
        else:
            _verify_graphical_programs(program, files, results, rerun_tests)

        if rerun_tests:

            def _contained_in(prefix, iterable, reverse=False):
                for test_id in iterable:
                    if not reverse and test_id.startswith(prefix):
                        return True
                    if reverse and prefix.startswith(test_id):
                        return True
                return False

            def _prefix_rates(ids: list[str]):
                prefix_occurrences = {}
                for test_id in ids:
                    prefix = ""
                    for element in test_id.split("-"):
                        if prefix == "":
                            prefix = element
                        else:
                            prefix += "-" + element
                        if prefix not in prefix_occurrences:
                            prefix_occurrences[prefix] = 0
                        prefix_occurrences[prefix] += 1
                prefix_occurrences = {
                    k: v
                    for k, v in sorted(
                        prefix_occurrences.items(), key=lambda item: item[1], reverse=True
                    )
                }
                return prefix_occurrences

            def _reduce_to_globs(rerun_test_ids: list[str]) -> list[str]:
                """Reduces the list of test ids using globs if possible"""
                prefix_occurrences_rerun = _prefix_rates(rerun_test_ids)
                prefix_occurrences_all = _prefix_rates(all_test_ids)
                prefix_occurrences_rerun = {
                    k: v
                    for k, v in prefix_occurrences_rerun.items()
                    if prefix_occurrences_all[k] == v
                }
                prefixes = []
                for prefix, _ in prefix_occurrences_rerun.items():
                    if not _contained_in(prefix, prefixes, reverse=True):
                        prefixes.append(prefix)

                return [
                    f"{prefix}{'-*' if prefix not in all_test_ids else ''}" for prefix in prefixes
                ]

            rerun_flags.append(
                f"-p \"{program.id}\" -t \"{','.join(_reduce_to_globs(rerun_tests))}\""
            )

    if rerun_flags:
        print("\nTests with critical missing data:\n    " + "\n    ".join(rerun_flags) + "\n")

    return results
