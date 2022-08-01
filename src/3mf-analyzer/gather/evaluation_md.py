"""Builds a markdown representation of the testcase evaluations."""

from os.path import join
from textwrap import dedent, indent
from typing import Dict

from .. import EVALUATION_DIR, PROGRAMS_DIR, yaml
from ..utils import get_all_tests, get_all_tests_by_type
from .utils import format_spec_conformity, get_markdown_table


def _expect_fail(test_description):
    """Checks if test is supposed to error."""

    expect_fail = False

    spec_conform = test_description.get("conforms_to_spec")
    if spec_conform is not None:
        if spec_conform == "n" or spec_conform is False:
            return True
        if isinstance(spec_conform, dict):
            vals = ["invalid" in str(value).lower() for _, value in spec_conform.items()]
            expect_fail = all(vals)
            if "materials" in spec_conform:
                expect_fail = "invalid" in spec_conform["materials"].lower()
        if not isinstance(spec_conform, dict) or expect_fail is True:
            return expect_fail

    if "duplicate with the same ID" in test_description.get("further_infos", ""):
        return True

    name = test_description.get("name", "")
    if "vertices" in name or "triangles" in name:
        return True

    return expect_fail


def _is_failed(test_infos):
    if "aborted" in test_infos.get("status", "").lower():
        return True
    interpreted_status = test_infos.get("interpretation", {}).get("status")
    if interpreted_status in ("aborted", "loaded nothing"):
        return True
    return False


def _is_loaded(test_infos):
    if "loaded" in test_infos.get("status", "").lower():
        return True
    interpreted_status = test_infos.get("interpretation", {}).get("status")
    if interpreted_status == "loaded":
        return True
    return False


def _might_be_crashed(test_infos):
    for prop in ["status", "info"]:
        if "crash" in test_infos.get(prop, "").lower():
            return True
    return False


def _might_be_hanging(test_infos):
    for prop in [
        test_infos.get("status", ""),
        test_infos.get("info", ""),
        test_infos.get("interpretation", {}).get("status", ""),
    ]:
        if "hang" in prop.lower() or prop == "loading":
            return True
    return False


def _get_summary(infos, descriptions):

    predefined_summary_items = [
        "Not Empty Server Logs",
        "Manually Marked to be Re-Run",
        "Marked as Critical",
        "Loaded Basic XML Tests",
        "Loaded XML Attacks",
        "Possibly Crashed Tests",
        "Possibly Hanging Tests",
        "Statistical Outliers",
    ]
    summary = {}
    for item in predefined_summary_items:
        summary[item] = {program_id: [] for program_id in infos}

    success_fail_summary = {
        "Failed Expectedly": {},
        "Succeeded Unexpectedly": {},
        "Failed Unexpectedly": {},
        "Succeeded Expectedly": {},
    }

    def _add_item(collection, key, program_id, item):
        if key not in collection:
            collection[key] = {}
        if program_id not in collection[key]:
            collection[key][program_id] = []
        collection[key][program_id].append(item)

    for program_id, content in infos.items():
        for test_id, test_infos in content.get("tests", {}).items():

            if test_infos.get("server_log_interesting"):
                _add_item(summary, "Not Empty Server Logs", program_id, test_id)

            if test_infos.get("rerun"):
                _add_item(summary, "Manually Marked to be Re-Run", program_id, test_id)

            if test_infos.get("critical"):
                _add_item(summary, "Marked as Critical", program_id, test_id)

            if test_id.startswith("XML") and _is_loaded(test_infos):
                if "-B-" in test_id:
                    _add_item(summary, "Loaded Basic XML Tests", program_id, test_id)
                else:
                    _add_item(summary, "Loaded XML Attacks", program_id, test_id)

            if _might_be_crashed(test_infos):
                _add_item(summary, "Possibly Crashed Tests", program_id, test_id)

            if _might_be_hanging(test_infos):
                _add_item(summary, "Possibly Hanging Tests", program_id, test_id)

            if test_infos.get("interpretation", {}).get("is_outlier", False) is True:
                _add_item(summary, "Statistical Outliers", program_id, test_id)

            if not test_id.startswith("R"):
                _failed = _is_failed(test_infos)
                _fail_expected = _expect_fail(descriptions[test_id])
                if _failed is None:
                    _add_item(success_fail_summary, "Uncertain", program_id, test_id)
                elif _fail_expected and _failed:
                    _add_item(success_fail_summary, "Failed Expectedly", program_id, test_id)
                elif not _fail_expected and _failed:
                    _add_item(success_fail_summary, "Failed Unexpectedly", program_id, test_id)
                elif _fail_expected and not _failed:
                    _add_item(success_fail_summary, "Succeeded Unexpectedly", program_id, test_id)
                elif not _fail_expected and not _failed:
                    _add_item(success_fail_summary, "Succeeded Expectedly", program_id, test_id)

    section = "## Summary\n\n"

    section += "### Fail/Success Statistics\n\n"
    section += get_markdown_table(
        ["Program", *success_fail_summary.keys()],
        [
            [
                program_id,
                *[
                    len(program_ids.get(program_id, []))
                    for _, program_ids in success_fail_summary.items()
                ],
            ]
            for program_id in infos.keys()
        ],
        ["l", *["r"] * len(success_fail_summary)],
        always_return_table=True,
    )
    section += "\n"

    for key, programs in summary.items():
        section += f"### {key}\n\n"
        section += get_markdown_table(
            ["Program", "Count", "Tests"],
            [[program, len(tests), ", ".join(tests)] for program, tests in programs.items()],
            ["l", "r", "l"],
            always_return_table=True,
        )
        section += "\n"

    return section + "\n"


def _get_full_results(infos):
    def _get_manual_eval(program_id, test_id, program_info):
        test_data = program_info.get("tests", {}).get(test_id)
        if test_data is None:
            return ""

        result = test_data.get("status", "")

        if test_data.get("alert"):
            alert = test_data["alert"]
            if program_info.get("alerts") and alert in program_info.get("alerts"):
                _alert = f"[^{program_id}:{alert}]"
            else:
                _alert = alert.replace("\n", " ").strip()
            if alert.startswith("E"):
                alert_type = "error"
            if alert.startswith("W"):
                alert_type = "warning"
            if alert_type:
                result += f" w/ {alert_type} {_alert}"
            else:
                result += f" w/ {_alert}"

        if test_data.get("info"):
            info_msg = test_data.get("info").replace("\n", " ").strip()
            if info_msg != "TODO":
                result += f" ({info_msg})"

        return result

    def _get_auto_eval(test_id, program_info):
        test_data = program_info.get("tests", {}).get(test_id)
        if test_data is None:
            return ""

        result = test_data.get("interpretation", {}).get("status", "")

        if result == "loaded":
            result += f' ({test_data["image_similarity"]["similar_to"]["test_id"]})'

        return result

    def _type_to_section(
        nesting_level: int,
        type_name: str,
        type_description: str,
        contained_tests: Dict,
    ) -> str:
        section = f'{"#" * (nesting_level + 3)} {type_name}\n\n{type_description}\n'

        for test_id, data in contained_tests.items():
            section += f'{"#" * (nesting_level + 4)} {test_id}\n\n'
            section += f'**Name:** {data.get("name", "")}  \n'
            section += f'**Expected Behavior:** {data.get("expected_behavior", "")}  \n'
            section += f"**Spec Conformity:** {format_spec_conformity(data)}  \n"
            section += f'**Further Infos:** {data.get("further_infos", "")}  \n\n'
            table_rows = [
                [
                    program_id,
                    _get_manual_eval(program_id, test_id, program_info),
                    _get_auto_eval(test_id, program_info),
                ]
                for program_id, program_info in infos.items()
            ]
            section += get_markdown_table(
                ["Program", "Manual Evaluation", "Automatic Evaluation"],
                table_rows,
                ["l", "l", "l"],
            )
            section += "\n"
        return section

    return "## Full Results\n\n" + "\n\n".join(get_all_tests_by_type(callback=_type_to_section))


def build_evaluations_markdown():
    """Builds a markdown representation of the testcase evaluations."""

    with open(join(PROGRAMS_DIR, "config.yaml"), "r", encoding="utf8") as in_file:
        programs = yaml.load(in_file)
        program_ids = sorted([program["id"] for program in programs])

    all_test_descriptions = get_all_tests()

    infos = {}
    for program_id in program_ids:
        with open(join(EVALUATION_DIR, program_id, "info.yaml"), "r", encoding="utf8") as yaml_file:
            content = yaml.load(yaml_file)
        infos[program_id] = content

    output = "# Attacks/Tests Evaluation\n\n"

    output += _get_summary(infos, all_test_descriptions)

    output += _get_full_results(infos)
    # for program_id, content in infos.items():
    #     output += _get_evaluation_markdown_subsections(program_id, content)

    return output
