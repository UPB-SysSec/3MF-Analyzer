import argparse
import logging
import sys
from textwrap import dedent

from . import (
    build_main,
    build_parser,
    create_main,
    create_parser,
    evaluate_main,
    evaluate_parser,
    gather_main,
    gather_parser,
    run_main,
    run_parser,
    server_main,
    server_parser,
)


def main():
    command_mapping = {
        "create": (create_main, create_parser),
        "build": (build_main, build_parser),
        "run": (run_main, run_parser),
        "server": (server_main, server_parser),
        "evaluate": (evaluate_main, evaluate_parser),
        "gather": (gather_main, gather_parser),
    }

    # define main parser
    _usage = dedent(
        """\
        testbed <command> [<args>]

        The available commands are (use <command> -h/--help for more information):
        """
    )
    padding_size = len(max(command_mapping.keys(), key=len)) + 3
    for command, (_, parser) in command_mapping.items():
        _usage += f"    {command: <{padding_size}}{parser().description}\n"

    main_parser = argparse.ArgumentParser(
        description="Provides a number of scripts to handle the test automation of this project.",
        usage=_usage,
    )
    main_parser.add_argument("command", help="Subcommand to run")

    # parse command
    command = main_parser.parse_args(sys.argv[1:2]).command
    raw_args = sys.argv[2:]

    # parse command's arguments and call appropriate functions
    _command = command_mapping.get(command)
    if _command is not None:
        _main, _parser = _command
        parser: argparse.ArgumentParser = _parser()
        parser.prog = f"testbed {command}"
        args = vars(parser.parse_args(raw_args))
        if args:
            logging.debug("Parsed arguments: %s", args)
            _main(args)
        else:
            _main()
    else:
        print(f"No such {command=}")


if __name__ == "__main__":
    main()
