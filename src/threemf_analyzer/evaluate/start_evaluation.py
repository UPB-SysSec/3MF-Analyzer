from .arg_parser import sanitize_args
from .interpret import interpret_data
from .manual import show_screenshots
from .screenshots import compare_screenshots


def main(parsed_arguments: dict[str, str]) -> None:
    program_ids, test_ids = sanitize_args(parsed_arguments)

    if parsed_arguments["enable_automatic"]:
        compare_screenshots(program_ids, test_ids)

    if parsed_arguments["enable_manual"]:
        show_screenshots(program_ids, test_ids)

    if parsed_arguments["enable_interpretation"]:
        interpret_data(program_ids, test_ids)
