"""Handles the CLI arguments for this command."""

import argparse


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Gathers the testcases and results into readable Markdown."
    )

    return parser
