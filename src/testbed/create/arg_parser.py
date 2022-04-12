"""Handles the CLI arguments for this command."""

import argparse


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Creates/Generates testcases into /src/testcases/generated "
        "(usually only required to run once on every system or if you change the generation code)."
    )
    parser.add_argument(
        "-x",
        "--disable-xml-based",
        action="store_true",
        help="Disables the generation of the XML-based (general XML) testcases.",
    )
    parser.add_argument(
        "-m",
        "--disable-mutation-based",
        action="store_true",
        help="Disables the generation of the mutation-based testcases.",
    )

    return parser
