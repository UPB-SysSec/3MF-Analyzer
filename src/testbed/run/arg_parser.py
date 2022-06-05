"""Handles the CLI arguments for this command."""

import argparse
from typing import List, Tuple

from .. import yaml
from ..dataclasses import File, Program
from ..utils import parse_programs, parse_tests


def sanitize_args(args: dict) -> Tuple[List[int], List[Program], List[File]]:
    """Verifies the parsed arguments and converts glob and
    "all" statements to actual tests/programs."""

    snapshot_intervals = [int(sec) for sec in args["snapshot_intervals"].split(",")]

    return snapshot_intervals, parse_programs(args["programs"]), parse_tests(args["tests"])


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Runs the given test file(s) with the given program(s) (only Windows)."
    )
    parser.add_argument(
        "-p",
        "--programs",
        help="ID's of the programs that should run the test files. Default `ALL` "
        "Will skip any program/ID that does not exist (according to the yaml). "
        'For multiple values use: "val1,val2,..."',
        default="ALL",
    )
    parser.add_argument(
        "-t",
        "--tests",
        help=parse_tests.__doc__,
        default="ALL",
    )
    parser.add_argument(
        "-s",
        "--snapshot-intervals",
        help="Seconds after starting the program to wait before taking a screenshot "
        "and storing the process data. Comma separated integer values. "
        "The count starts at the time of displaying the main window (as Windows recognizes it). "
        "Default: 0,3,7,10",
        default="0,3,7,10",
    )
    parser.add_argument(
        "--process-startup-timeout",
        help="Time to wait for the process to start before cancelling the try and "
        "continuing with the next test case. Default: 5s",
        default=5,
        type=int,
    )
    parser.add_argument(
        "--window-startup-timeout",
        help="Time to wait for the window to be ready before cancelling the try and "
        "continuing with the next test case. Default: 30s",
        default=30,
        type=int,
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
        help="Deletes the data of the specified programs/tests before running them.",
    )
    run_group.add_argument(
        "--data-update-only",
        action="store_true",
        help="Verifies the files that should be created with the other arguments. "
        "If there are broken/missing files, those are reported and you get "
        "a list of arguments with which to run this script to get the missing data. "
        "Happens anyway after a normal run, this skips the execution entirely. "
        "With this the program version will not be updated.",
    )

    return parser
