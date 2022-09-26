"""Handles the CLI arguments for this command."""

import argparse


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Builds the existing testcases into usable formats."
    )

    return parser
