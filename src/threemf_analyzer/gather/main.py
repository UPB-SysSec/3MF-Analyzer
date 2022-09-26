"""Builds a markdown representation of the information in /data"""

import logging
from os.path import join

from .. import DATA_DIR
from .description_md import build_descriptions_markdown
from .evaluation_md import build_evaluations_markdown


def build_md_files():
    """Builds a markdown representation of the gathered information"""

    prefix = (
        "<!-- This file is automatically generated, please to not change any content here. -->"
        "\n\n"
    )

    # logging.info("Write attack/test descriptions")
    # description_md = build_descriptions_markdown()
    # with open(join(DATA_DIR, "test-descriptions.md"), "w", encoding="utf8") as out_file:
    #     out_file.write(prefix + description_md)

    logging.info("Write attack/test evaluations")
    evaluation_md = build_evaluations_markdown()
    with open(join(DATA_DIR, "evaluation-results.md"), "w", encoding="utf8") as out_file:
        out_file.write(prefix + evaluation_md)