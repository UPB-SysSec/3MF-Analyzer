"""Exposes all relevant functions to the outside and provides paths for the package."""

import logging
from glob import glob
from os.path import abspath, dirname, join
from pathlib import Path

from ruamel.yaml import YAML

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)8s | %(name)s: %(message)s",
)

yaml = YAML()
yaml.preserve_quotes = True

# root directory of this repository
ROOT_DIR = abspath(join(dirname(__file__), "..", ".."))

# directories in the src folder
SFTA_DIR = join(ROOT_DIR, "src", "PS-SFTA")
LIB3MF_DIR = join(ROOT_DIR, "src", "lib3mf_sdk_v2.1.1")
TESTFILE_SRC_DIR = join(ROOT_DIR, "src", "testcases")
TESTFILE_GENERATED_SRC_DIR = join(TESTFILE_SRC_DIR, "generated")

# build directory
BUILD_DIR = join(ROOT_DIR, "build")

# directories in the data directory
DATA_DIR = join(ROOT_DIR, "data")
DESCRIPTION_DIR = join(DATA_DIR, "description")
DESCRIPTION_GLOB = join(DESCRIPTION_DIR, "[0-9]*_*.yaml")
EVALUATION_DIR = join(DATA_DIR, "evaluation")
PROGRAMS_DIR = join(DATA_DIR, "programs")
# maps the 3MF specifications to the existing XSD file paths
XSD_FILES = {
    Path(path).stem.replace("3mf-", ""): path for path in glob(join(DATA_DIR, "xsd", "3mf-*.xsd"))
}

# infos for the simple HTTP server (needed for some attacks)
STATIC_FILE_DIR_SRC = join(TESTFILE_SRC_DIR, "server_files")
STATIC_FILE_DIR_DST = join(BUILD_DIR, "server_files")
SERVER_PORT = 8080
SERVER_NAME = "localhost"
LOCAL_SERVER = f"http://{SERVER_NAME}:{SERVER_PORT}"


from .build import build_main, build_parser
from .create import create_main, create_parser
from .evaluate import evaluate_main, evaluate_parser
from .gather import gather_main, gather_parser
from .run import run_main, run_parser
from .server import server_main, server_parser
