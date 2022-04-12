"""Handles the CLI arguments for this command."""

import argparse
from typing import List, Tuple

from ..utils import parse_programs, parse_tests


def sanitize_args(args: dict) -> Tuple[List[str], List[str]]:
    """Sanitizes the program and test args."""
    programs = parse_programs(args["programs"])
    files = parse_tests(args["tests"])

    program_ids = [program.id for program in programs]
    test_ids = [file.test_id for file in files]
    return program_ids, test_ids


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Evaluates the data produced by the run command.",
    )
    parser.add_argument(
        "-p",
        "--programs",
        help="ID's of the programs where the results would be evaluated. Default `ALL`. "
        "Will skip any program/ID that does not exist "
        "(according to the yaml or the existing folders in /data/evaluation). "
        'For multiple values use: "val1,val2,..."',
        default="ALL",
    )
    parser.add_argument(
        "-t",
        "--tests",
        help="ID's of the tests that should be evaluated. Default `ALL`. "
        "Will skip any test/ID that could not be found or that has not been created "
        "(according to the yaml). "
        'For multiple values use: "val1,val2,...". '
        "Globbing is possible, but very restricted: * at the end of a partial ID will be "
        "recognized and all matching tests will be added.",
        default="ALL",
    )

    parser.add_argument(
        "-a",
        "--enable-automatic",
        action="store_true",
        help="Automatically evaluates the data. "
        "Compares screenshots from run command with reference screenshots.",
    )
    parser.add_argument(
        "-m",
        "--enable-manual",
        action="store_true",
        help="Shows the screenshots of the specified programs/tests. "
        "Allows to write comments (further_infos field) and to "
        "mark the test as 'done' or 'not done' so it will be re-run, or not.",
    )
    parser.add_argument(
        "-i",
        "--enable-interpretation",
        action="store_true",
        help="Interprets the evaluation results.",
    )

    return parser
