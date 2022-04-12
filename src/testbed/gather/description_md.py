"""Builds a markdown representation of the testcase descriptions."""

from glob import glob
from os.path import join
from textwrap import dedent, indent
from typing import Dict, overload

from .. import DESCRIPTION_DIR, DESCRIPTION_GLOB, yaml
from ..utils import get_all_tests_by_type
from .utils import get_markdown_table


def _types_to_markdown_sections(types: Dict) -> str:
    def _format_spec_conformity(data):
        conforms_to_spec = data.get("conforms_to_spec", "")
        if isinstance(conforms_to_spec, str):
            return conforms_to_spec

        res = []
        for spec, value in conforms_to_spec.items():
            res.append(f"{spec}: {value.split(':')[0]}")
        return "; ".join(res)

    def _types_to_sections(types: Dict, section_level: int = 2, is_top_leven_section=False) -> str:
        res = ""
        for type_name, infos in types.items():
            res += _type_to_section(
                section_level,
                type_name,
                infos.get("description", ""),
                infos.get("tests", {}),
                is_top_leven_section=False if "subtypes" in infos else is_top_leven_section,
            )
            if "subtypes" in infos:
                res += _types_to_sections(infos["subtypes"], section_level=section_level + 1)
        return res

    table_headers = [
        "ID",
        "Name (Attack/Test)",
        "Scope",
        "Spec Conform",
        "Expected Behavior",
        "Created",
        "Description/Information/Idea/TODO",
    ]
    table_alignments = ["l", "l", "l", "c", "l", "c", "l"]

    def _type_to_section(
        section_level: int,
        type_name: str,
        type_description: str,
        tests: Dict,
        is_top_leven_section=False,
    ) -> str:
        section = f'{"#" * section_level} {type_name}\n\n{type_description}\n'
        table_rows = [
            [
                id_,
                data.get("name", ""),
                data.get("scope", ""),
                _format_spec_conformity(data),
                data.get("expected_behavior", ""),
                "x" if data.get("created") else "",
                data.get("further_infos", ""),
            ]
            for id_, data in tests.items()
        ]
        section += get_markdown_table(
            table_headers,
            table_rows,
            table_alignments,
            always_return_table=is_top_leven_section,
        )
        section += "\n"
        return section

    return _types_to_sections(types, is_top_leven_section=True)


def _scopes_to_markdown_text(scopes: Dict) -> str:
    res = ""
    for scope, description in scopes.items():
        res += f"- **{scope}**:\n"
        res += indent(description, prefix="  ")
        res += "\n"
    return res


def _footnotes_to_markdown_text(footnotes: Dict) -> str:
    res = ""
    for fn_id, info in footnotes.items():
        res += f"[^{fn_id}]:\n"
        res += indent(info, prefix="    ")
        res += "\n"
    return res


def _get_statistical_overview():
    """Creates an statistical overview of the tests in each type"""

    def _type_to_section(
        nesting_level: int,
        type_name: str,
        type_description: str,
        contained_tests: Dict,
    ) -> str:
        # section = f'{"#" * (nesting_level + 2)} {type_name}\n\n'

        stats = {
            "Total Nr. Tests": len(contained_tests),
            "Nr. Generated": 0,
            "3D Manufacturing Format": 0,
            "3D Model Part": 0,
            "XML": 0,
            "ZIP": 0,
        }

        for test_id, data in contained_tests.items():
            if test_id.startswith("GEN"):
                stats["Nr. Generated"] += 1
            if data.get("scope") is not None:
                stats[data["scope"]] += 1

        # section += get_markdown_table(
        #     ["Property", "Number of Tests"],
        #     [[key, value] for key, value in stats.items()],
        #     ["l", "l"],
        # )

        return (nesting_level, type_name, stats)

    overall_stats = {}
    parent_type_name = ""
    for nesting_level, type_name, stats in get_all_tests_by_type(callback=_type_to_section):
        if nesting_level == 0:
            parent_type_name = type_name
            overall_stats[type_name] = {}
        for stat_name, stat_value in stats.items():
            if stat_name not in overall_stats[parent_type_name]:
                overall_stats[parent_type_name][stat_name] = 0
            overall_stats[parent_type_name][stat_name] += stat_value

    result = "# Statistical Overview\n\n"
    for type_name, stats in overall_stats.items():
        result += (
            get_markdown_table(
                [type_name, "Amount"],
                [[key, value] for key, value in stats.items()],
                ["l", "l"],
            )
            + "\n"
        )

    return result


def build_descriptions_markdown():
    """Builds a markdown representation of the testcase descriptions."""

    output = _get_statistical_overview()
    output += "\n\n"

    with open(join(DESCRIPTION_DIR, "description_texts.yaml"), "r", encoding="utf-8") as in_file:
        description_texts = yaml.load(in_file)

    types, footnotes = get_all_tests_by_type(get_footnotes=True)

    output += dedent(
        """\
            # Attacks/Tests Details (by Type)

            This sections lists all, currently available, attacks and tests by the type of attack/test they perform.
            The following sections denote the types and subtypes.
            Each type has a brief description off the attack/test vector and a table of all attacks/tests with that type.

            All footnotes that appear in the tables (look like this in raw text: `[^footnote-id]`) are at the end of this section in raw text format.

            The table has the following columns:

            - **ID** is a unique identifier for a test case.
              It matches the file in the `src/testcases` folder and usually consists of some combination if Name, Scope and Type of the test case.
            - **Name** is a name of the test case and usually give a basic idea of what is attacked/tested.
            - **Scope** denotes a specification (or part of a specification) that is targeted/used for the attack.
            - **Spec Conform** states whether, or not, the attack/test conforms to the 3MF specification.
              A simple "y"/"n" (yes/no) is in regards to the 3MF specification as a whole.
              If the y/n value is appended with a "(?)" there is an uncertainty associated (that is usually specified in the "Description/Information/Idea/TODO" field.)
              If there is a value like `core: ..., materials: ...` there was no *manual* evaluation of the specification validity.
              In these cases, the test cases were automatically generated and validated against the XSD for their specification extension and the core specification.
              Possible values are: "Invalid XML", "Invalid 3MF", "Valid".
              As the materials specification redefines parts of the core specification (and add required attributes that are not in their own scope) the core specification will always evaluate "Invalid 3MF" even if the file is valid according to the materials extension.
            - **Expected Behavior** states the behavior we would prefer a program would *optimally* have in this case.
            - **Created** states whether the test case exists/ was created.
            - **Description/Information/Idea/TODO** adds any additional information that might be of interest/value.

            The scopes are described as follows:\n
        """
    )
    output += _scopes_to_markdown_text(description_texts["scopes"])
    output += _types_to_markdown_sections(types)
    output += _footnotes_to_markdown_text(footnotes)
    return output
