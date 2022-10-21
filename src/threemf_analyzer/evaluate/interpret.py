"""Interprets the information collected by the automatic and manual evaluation."""
import logging
from os.path import isfile, join

from .. import EVALUATION_DIR, yaml


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


def _interpret(program_id: str, test_ids: list[str]) -> None:
    """"""
    logging.info("%s | Start interpretation", program_id)
    program_dir_path = join(EVALUATION_DIR, program_id)

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
        test_data["interpretation"] = {
            "status": status,
            "is_outlier": _is_outlier(stats, test_id, test_data),
            "confidence": confidence,
        }

    with open(join(program_dir_path, "info.yaml"), "w", encoding="utf8") as yaml_file:
        yaml.dump(content, yaml_file)


def interpret_data(program_ids: list[str], test_ids: list[str]) -> None:
    """Compares all testcases of all given programs with the references cases.
    For more infos see: `_compare_to_reference_cases` function."""

    for program_id in program_ids:
        _interpret(program_id, test_ids)
