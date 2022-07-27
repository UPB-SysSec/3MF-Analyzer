"""Builds the data from src into files in build"""

import logging
import shutil
from glob import glob
from os import listdir, walk
from os.path import isdir, isfile, join
from pathlib import Path
from zipfile import ZipFile

from .. import BUILD_DIR, DATA_DIR, TESTFILE_SRC_DIR, yaml
from .dataclasses import Folder


def _gather_test_data(in_dir: str, out_dir: str):
    """Gather and convert test data, move/copy it to a temp directory (log_dir)."""

    def __gather_test_data(dir_level):
        """Recursively gathers the test data, each call handles a single level of nesting.
        If a directory has no "filetype" it is handled as a nesting level."""

        logging.info("Gathering test data in %s", dir_level)
        src_path = join(in_dir, dir_level)
        dst_path = join(out_dir, dir_level)
        Path(src_path).mkdir(parents=True, exist_ok=True)
        Path(dst_path).mkdir(parents=True, exist_ok=True)

        filepaths = []

        for entry in listdir(src_path):
            entry_path = join(src_path, entry)
            if isfile(entry_path):
                filepaths.append(shutil.copy(entry_path, dst_path))
            elif isdir(entry_path):
                filetypes = entry.split(".")[1:]
                if filetypes == []:
                    res = __gather_test_data(join(dir_level, entry))
                    filepaths += res

                for filetype in filetypes:
                    folder = Folder(
                        filetype=filetype,
                        src_path=join(src_path, entry),
                        foldername=entry.split(".")[0],
                        dst_path=dst_path,
                    )
                    filepaths += _build_file_from_folder(folder=folder)

        return filepaths

    return __gather_test_data("")


def _build_file_from_folder(folder: Folder):
    """Hooks into the testfile creation."""

    if folder.filetype == "ignore":
        return []

    # Takes a folder description for 3mf files and archives it accordingly.
    if folder.filetype == "3mf":

        files_in_dir = [
            join(folder, file_name)
            for folder, _, files in walk(folder.src_path)
            for file_name in files
        ]

        dst_path_file = join(folder.dst_path, folder.foldername + "." + folder.filetype)
        try:
            with ZipFile(dst_path_file, "w") as zip_file:
                for file_name in files_in_dir:
                    zip_file.write(
                        file_name,
                        arcname=file_name.replace(f"{folder.src_path}", "")[1:],
                    )
        except ValueError as err:
            logging.warning("Error while writing %s", dst_path_file)
            logging.error(err)

        return [dst_path_file]

    # Creates 3MF files in bulk for changes to the model/relations file.
    if folder.filetype == "3mf_models" or folder.filetype == "3mf_rels":

        if folder.filetype == "3mf_models":
            file_ending = ".model"
            folder_name = "3D"
            target_filename = "3dmodel.model"

        if folder.filetype == "3mf_rels":
            file_ending = ".rels"
            folder_name = "_rels"
            target_filename = ".rels"

        skeleton_path = join(folder.src_path, "skeleton")
        skeleton_files = [
            join(folder, file_name)
            for folder, _, files in walk(skeleton_path)
            for file_name in files
        ]

        model_files = [
            file_name
            for file_name in listdir(folder.src_path)
            if Path(file_name).suffix == file_ending
        ]

        out_dir = join(folder.dst_path, folder.foldername)
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        model_file_paths = []
        for model_file in model_files:
            dst_path_file = join(out_dir, model_file.replace(file_ending, ".3mf"))
            model_file_paths.append(dst_path_file)

            try:
                with ZipFile(dst_path_file, "w") as zip_file:
                    for file_name in skeleton_files:
                        archive_filename = file_name.replace(f"{skeleton_path}", "")[1:]
                        if archive_filename != join(folder_name, target_filename):
                            zip_file.write(file_name, arcname=archive_filename)

                    zip_file.write(
                        join(folder.src_path, model_file),
                        arcname=join(folder_name, target_filename),
                    )
            except ValueError as err:
                logging.warning("Error while writing %s", dst_path_file)
                logging.error(err)

        return model_file_paths


def _modify_test_description(build_dir: str, file_path: str):
    """Calls all functions that modify a single test description yaml."""

    def _check_if_testfiles_exist(content):
        """Checks for each described test whether or not a testfile exists in the build folder.
        The filename has to start with the test ID."""

        existing_filenames = []
        for _, _, filenames in walk(build_dir):
            existing_filenames += filenames

        def __file_exists(test_id):
            for name in existing_filenames:
                if name.lower().startswith(test_id.lower()):
                    return True
            return False

        for test_id in content.get("tests", {}):
            content["tests"][test_id]["created"] = __file_exists(test_id)

        return content

    with open(file_path, "r", encoding="utf8") as yaml_file:
        content = yaml.load(yaml_file)

    content = _check_if_testfiles_exist(content)

    with open(file_path, "w", encoding="utf8") as yaml_file:
        yaml.dump(content, yaml_file)


def _modify_all_test_descriptions(build_dir: str, data_dir: str):
    """Updates all test description files after the build was completed."""
    for file in sorted(glob(join(data_dir, "description", "[0-9]*_*.yaml"))):
        _modify_test_description(build_dir, file)


def build_testfiles() -> None:
    """Builds the files in in_dir to out_dir according to the rules in `build_file_from_folder`.
    Updates the test descriptions in data_dir"""

    in_dir, out_dir, data_dir = TESTFILE_SRC_DIR, BUILD_DIR, DATA_DIR

    try:
        shutil.rmtree(out_dir)
    except FileNotFoundError:
        pass
    reported_files = _gather_test_data(in_dir, out_dir)
    actual_files = [
        join(folder, file_name) for folder, _, files in walk(out_dir) for file_name in files
    ]

    if sorted(reported_files) != sorted(actual_files):
        if len(reported_files) > len(actual_files):
            logging.warning(
                "Some files were not build: %s", set(reported_files) - set(actual_files)
            )
        if len(reported_files) < len(actual_files):
            logging.warning(
                "More files build than expected: %s", set(actual_files) - set(reported_files)
            )

    _modify_all_test_descriptions(out_dir, data_dir)
