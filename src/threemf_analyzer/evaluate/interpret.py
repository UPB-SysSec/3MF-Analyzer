"""Interprets the information collected by the automatic and manual evaluation."""
import logging
from os.path import isfile, join

from .. import EVALUATION_DIR, yaml
from ..utils import get_all_tests, get_tests_type_and_scope, reduce_test_ids_to_globs
from .utils import expect_fail


def _get_status(test_infos, ref_screenshots_config):
    status = "indecisive"
    confidence = "none"
    confidence_boundaries = (("high", 0.99), ("medium", 0.9), ("low", 0.8))

    def __get_ref_screenshot_ids(type_name: str):
        for screenshot_id in ref_screenshots_config.get(type_name, []):
            if screenshot_id != "none":
                yield screenshot_id

    if "image_similarity" in test_infos:
        image_similarity = test_infos["image_similarity"]
        similar_test_id = image_similarity["similar_to"]["test_id"]
        score = float(image_similarity["score"])

        for _confidence, boundary in confidence_boundaries:
            if score > boundary:
                confidence = _confidence
                break

        if confidence == "high":
            if similar_test_id in ["R-ERR", *__get_ref_screenshot_ids("error")]:
                return "aborted", confidence
            if similar_test_id in __get_ref_screenshot_ids("warning"):
                return "loaded /w warning", confidence
            if similar_test_id in __get_ref_screenshot_ids("loading"):
                return "loading", confidence
            if similar_test_id in __get_ref_screenshot_ids("empty"):
                return "loaded nothing", confidence
            if similar_test_id in __get_ref_screenshot_ids("rerun"):
                test_infos["rerun"] = True
                return "indecisive", "none"

            status = "loaded"

    if test_infos.get("critical") is True and not test_infos.get("rerun") is True:
        return "aborted", "high"

    return status, confidence


def _get_statistics(tests):
    def increment(_dict, key):
        if key not in _dict:
            _dict[key] = 0
        _dict[key] += 1

    stats = {
        "nr_tests": 0,
        "nr_problems": {},
        "problem_occurrences": {},
        "nr_missing_process_info": {},
        "nr_missing_screenshot": {},
    }

    for test_id, test_data in tests.items():
        if test_id.startswith("R"):
            continue

        increment(stats, "nr_tests")
        increment(stats["nr_problems"], len(test_data.get("problems", [])))
        for problem in test_data.get("problems", []):
            increment(stats["problem_occurrences"], problem)
        increment(stats["nr_missing_process_info"], test_data.get("missing_process_info", 0))
        increment(stats["nr_missing_screenshot"], test_data.get("missing_screenshot", 0))

    return stats


def _is_outlier(stats, test_id, test_data):
    def _is_high_value(all_values, target):
        """Determines if target is an especially high value or not.
        (Above 90th percentile)."""
        if not isinstance(target, int):
            target = len(target)

        smaller_values = [count for number, count in all_values.items() if number < target]
        if smaller_values == []:
            return False

        return (sum(smaller_values) / sum(all_values.values())) > 0.9

    for stat_name, value in stats.items():
        if stat_name.startswith("nr_") and isinstance(value, dict):
            if _is_high_value(value, test_data.get(stat_name[3:], 0)):
                return True

    return False


def _set_result(program_id, test_id, test_scope, test_type, evaluation_results, test_description):
    # using the attributes from .utils.Result as string values for results in YAML
    output_dir = join(EVALUATION_DIR, program_id, "snapshots", test_id)
    if test_type in ["Reference", "Functionality", "Miscellaneous"]:
        evaluation_results["result_interpretation"] = {
            "result": "NO_INFORMATION",
            "reason": "informational test case",
        }
        return

    if test_type == "Denial of Service":
        if (status := evaluation_results.get("status")) is not None:
            if status == "loading" or status == "crashed":
                evaluation_results["result_interpretation"] = {
                    "result": "VULNERABLE",
                    "reason": "status is 'loading' or 'crashed'",
                }
                return
        if (interpretation := evaluation_results.get("image_interpretation")) is not None:
            if (
                interpretation.get("status") == "aborted"
                and interpretation.get("confidence") == "high"
            ):
                evaluation_results["result_interpretation"] = {
                    "result": "NOT_VULNERABLE",
                    "reason": "status is 'aborted', so DOS didn't work",
                }
                return

    if test_type == "UI Spoofing":
        target_test = None
        match_target = None
        if test_id.startswith("GEN"):
            spec = test_id.split("-")[1]
            target_test = f"R-SPEC-{spec}-0"
            match_target = False
        if test_scope == "XML":
            target_test = "R-CYL"
            match_target = True
        if test_scope == "OPC":
            if test_id.startswith("OPC-LFI"):
                target_test = "R-CUB"
                match_target = True

        if (
            match_target is not None
            and target_test is not None
            and evaluation_results.get("image_interpretation", {}).get("status") == "loaded"
            and evaluation_results.get("image_interpretation", {}).get("confidence") == "high"
        ):
            if expect_fail(test_description):
                evaluation_results["result_interpretation"] = {
                    "result": "PARTIALLY_VULNERABLE",
                    "reason": "a model was loaded when 'fail' was expected",
                }
                return

            if not match_target:
                if (
                    evaluation_results.get("image_similarity", {})
                    .get("similar_to", {})
                    .get("test_id")
                    != target_test
                ):
                    evaluation_results["result_interpretation"] = {
                        "result": "VULNERABLE",
                        "reason": "the parsed model diverges from the intended output",
                    }
                    return

            else:
                if (
                    evaluation_results.get("image_similarity", {})
                    .get("similar_to", {})
                    .get("test_id")
                    == target_test
                ):
                    evaluation_results["result_interpretation"] = {
                        "result": "VULNERABLE",
                        "reason": "the parsed model includes to spoofed input",
                    }
                    return

    if test_type == "Data Exfiltration":
        # oob
        if evaluation_results.get("server_log_interesting"):
            serverlog_file_path = join(output_dir, "local-server.log")
            with open(serverlog_file_path, encoding="utf-8") as logfile:
                server_log = logfile.read()
                if "successful" in server_log:
                    evaluation_results["result_interpretation"] = {
                        "result": "VULNERABLE",
                        "reason": "string 'successful' found in server log",
                    }
                    return

    evaluation_results["result_interpretation"] = {
        "result": "NO_INFORMATION",
        "reason": "no information could be derived from the recorded data",
    }


def _interpret(program_id: str, test_ids: list[str]) -> None:
    """"""
    logging.info("%s | Start interpretation", program_id)
    program_dir_path = join(EVALUATION_DIR, program_id)
    all_tests = get_all_tests()
    all_tests_scope_type = get_tests_type_and_scope(
        ["Denial of Service", "UI Spoofing", "Data Exfiltration"]
    )

    with open(join(program_dir_path, "info.yaml"), "r", encoding="utf8") as yaml_file:
        content = yaml.load(yaml_file)
        tests = content.get("tests")
        if tests is None:
            return

    _screenshot_config_path = join(program_dir_path, "reference_screenshots", "config.yaml")
    if isfile(_screenshot_config_path):
        with open(_screenshot_config_path, "r", encoding="utf8") as yaml_file:
            ref_screenshots_config = yaml.load(yaml_file)
    else:
        ref_screenshots_config = {}

    stats = _get_statistics(tests)

    for test_id in test_ids:
        test_data = tests.get(test_id)
        if test_data is None:
            continue

        status, confidence = _get_status(test_data, ref_screenshots_config)
        if test_data["interpretation"]:
            del test_data["interpretation"]
        test_data["image_interpretation"] = {
            "status": status,
            "is_outlier": _is_outlier(stats, test_id, test_data),
            "confidence": confidence,
        }
        if test_id in all_tests_scope_type:
            _set_result(
                program_id,
                test_id,
                *all_tests_scope_type[test_id],
                test_data,
                all_tests.get(test_id),
            )

    with open(join(program_dir_path, "info.yaml"), "w", encoding="utf8") as yaml_file:
        yaml.dump(content, yaml_file)

    rerun_tests = []
    for test_id, test_data in tests.items():
        if test_data.get("rerun") is True:
            rerun_tests.append(test_id)
    return rerun_tests


def interpret_data(program_ids: list[str], test_ids: list[str]) -> None:
    """Compares all testcases of all given programs with the references cases.
    For more infos see: `_compare_to_reference_cases` function."""

    rerun_flags = []
    all_test_ids = get_all_tests().keys()

    for program_id in program_ids:
        rerun_tests = _interpret(program_id, test_ids)
        if rerun_tests:
            rerun_flags.append(
                f'-p "{program_id}" '
                f"-t \"{','.join(reduce_test_ids_to_globs(all_test_ids, rerun_tests))}\""
            )

    if rerun_flags:
        print("\nTests marked to rerun:\n    " + "\n    ".join(rerun_flags) + "\n")
