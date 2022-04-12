"""Differrent utility functions."""


def inline_blockquote(text: str):
    """Converts a markdown blockquote string to an inline quote:

    > abc     gets     "abc def"
    > def
    """
    result = []
    bq_started = False
    for line, next_line in zip(text.split("\n"), text.split("\n")[1:] + [""]):
        if line.strip().startswith("> "):
            if not bq_started:
                line = '"' + line[2:]
                bq_started = True
            else:
                line = line[2:]
            if not next_line.strip().startswith("> "):
                line += '"'
                bq_started = False
        result.append(line)
    return "\n".join(result)


def get_markdown_table(headers, rows, alignments, always_return_table=False):
    """Returns a formatted markdown table (pipe style) based on the given rows.
    Rows should be list of list (or tuples), where the first entry is a header row.
    Basically like CSV but in Python iterables.

    If the rows are empty and always_return_table is True an empty table is returned.
    Otherwise a placeholder text in HTML comments is returned."""

    if len(rows) == 0 and not always_return_table:
        return "<!-- This attack/test type has no direct entries. -->\n"

    for row in rows:
        for column_nr, _ in enumerate(headers):
            row[column_nr] = inline_blockquote(str(row[column_nr])).replace("\n", " ").strip()

    # max lengths of all columns in the table
    max_lengths = [max(len(header), 3) for header in headers]
    for row in rows:
        for column_nr, data in enumerate(row):
            if len(data) > max_lengths[column_nr]:
                max_lengths[column_nr] = len(data)

    def align(column_nr, text):
        if alignments[column_nr] == "l":
            return text.ljust(max_lengths[column_nr])
        if alignments[column_nr] == "r":
            return text.rjust(max_lengths[column_nr])
        if alignments[column_nr] == "c":
            return text.center(max_lengths[column_nr])

    table = []
    table.append([align(nr, text) for nr, text in enumerate(headers)])

    _header_line = []
    for column_nr, _ in enumerate(headers):
        if alignments[column_nr] == "l":
            _header_line.append(f":{'-' * (max_lengths[column_nr] - 1)}")
        if alignments[column_nr] == "r":
            _header_line.append(f"{'-' * (max_lengths[column_nr] - 1)}:")
        if alignments[column_nr] == "c":
            _header_line.append(f":{'-' * (max_lengths[column_nr] - 2)}:")
    table.append(_header_line)

    for row in rows:
        table.append([align(nr, text) for nr, text in enumerate(row)])

    markdown_table = ""
    for row in table:
        markdown_table += f"| {' | '.join(row)} |\n"

    return markdown_table


def format_spec_conformity(test_data):
    """Formats the specification conformity value to a string."""
    conforms_to_spec = test_data.get("conforms_to_spec", "")
    if isinstance(conforms_to_spec, str):
        return conforms_to_spec

    res = []
    for spec, value in conforms_to_spec.items():
        res.append(f"{spec}: {value.split(':')[0]}")
    return "; ".join(res)
