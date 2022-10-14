"""Handles the CLI arguments for this command."""

import argparse

from ..dataclasses import File
from ..utils import parse_programs, parse_tests
from .programs.base import Program


def sanitize_args(args: dict) -> tuple[list[int], list[type[Program]], list[File]]:
    """Verifies the parsed arguments and converts glob and
    "all" statements to actual tests/programs."""

    return parse_programs(args["programs"]), parse_tests(args["tests"])


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Runs the given test file(s) with the given program(s) (only Windows)."
    )
    parser.add_argument(
        "-p",
        "--programs",
        help=parse_programs.__doc__,
        default="ALL",
    )
    parser.add_argument(
        "-t",
        "--tests",
        help=parse_tests.__doc__,
        default="ALL",
    )

    run_group = parser.add_mutually_exclusive_group()
    run_group.add_argument(
        "--clear",
        action="store_true",
        help="Deletes the data of the specified programs/tests instead of running them.",
    )
    run_group.add_argument(
        "--clear-and-run",
        action="store_true",
        default=True,
        help="Deletes the data of the specified programs/tests before running them.",
    )
    run_group.add_argument(
        "--data-update-only",
        action="store_true",
        help="Verifies the files that should be created with the other arguments. "
        "If there are broken/missing files, those are reported and you get "
        "a list of arguments with which to run this script to get the missing data. "
        "Happens anyway after a normal run, this skips the execution entirely.",
    )

    return parser
