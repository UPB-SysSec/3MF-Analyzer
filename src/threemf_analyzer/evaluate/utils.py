"""Number of small util functions for interpretation of test cases/results."""

import json
from os.path import isfile, join

from .. import EVALUATION_DIR


class Result:
    """Result of a test case."""

    NO_INFORMATION = 0
    NOT_VULNERABLE = 1
    PARTIALLY_VULNERABLE = 2
    VULNERABLE = 3


def expect_fail(test_description):
    """Checks if test is supposed to error."""

    _expect_fail = False

    spec_conform = test_description.get("conforms_to_spec")
    if spec_conform is not None:
        if spec_conform == "n" or spec_conform is False:
            return True
        if isinstance(spec_conform, dict):
            vals = ["invalid" in str(value).lower() for _, value in spec_conform.items()]
            _expect_fail = all(vals)
            if "materials" in spec_conform:
                _expect_fail = "invalid" in spec_conform["materials"].lower()
        if not isinstance(spec_conform, dict) or _expect_fail is True:
            return _expect_fail

    if "duplicate with the same ID" in test_description.get("further_infos", ""):
        return True

    name = test_description.get("name", "")
    if "vertices" in name or "triangles" in name:
        return True

    return _expect_fail


def is_failed(program_id, test_id, test_infos):
    if "aborted" in test_infos.get("status", "").lower():
        return True

    if (interpretation := test_infos.get("image_interpretation", {})) is not None:
        if (
            interpretation.get("status") in ("aborted", "loaded nothing")
            and interpretation.get("confidence") == "high"
        ):
            return True

    return False


def is_loaded(program_id, test_id, test_infos):
    if "loaded" in test_infos.get("status", "").lower():
        return True

    if (interpretation := test_infos.get("image_interpretation", {})) is not None:
        if interpretation.get("status") == "loaded" and interpretation.get("confidence") == "high":
            return True

    return False


def is_crashed(program_id, test_id, test_infos):
    for prop in ["status", "info"]:
        if "crash" in test_infos.get(prop, "").lower():
            return True
    output_dir = join(EVALUATION_DIR, program_id, "snapshots", test_id, "test_run_data.json")
    test_run_data_path = join(output_dir, "test_run_data.json")
    if isfile(test_run_data_path):
        with open(test_run_data_path, encoding="utf-8") as test_data_file:
            test_run_data = json.load(test_data_file)
        if (
            exceptions := test_run_data.get("states", {})
            .get("05 model-not-loaded", {})
            .get("related_exception")
        ):
            if "<class 'selenium.common.exceptions.NoSuchWindowException'>" in exceptions:
                return True
    return False


def is_hanging(program_id, test_id, test_infos):
    for prop in [test_infos.get("status", ""), test_infos.get("info", "")]:
        if "hang" in prop.lower() or "loading" in prop.lower():
            return True

    if (interpretation := test_infos.get("image_interpretation", {})) is not None:
        if interpretation.get("status") == "loading" and interpretation.get("confidence") == "high":
            return True

    return False
