"""Handles the CLI arguments for this command."""

import argparse


def get_parser() -> argparse.ArgumentParser:
    """Parses the arguments for this command"""

    parser = argparse.ArgumentParser(
        description="Starts an HTTP Server. This should be executed in parallel to the run command."
    )

    return parser
