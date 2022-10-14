"""Compares screenshots of testcases with the screenshots of references cases."""

import logging
import signal
from glob import glob
from multiprocessing import Manager, Pool, Queue
from os import listdir
from os.path import isdir, join
from pathlib import Path

import numpy as np
from skimage.io import imread
from skimage.metrics import structural_similarity
from skimage.transform import resize

from .. import DESCRIPTION_GLOB, EVALUATION_DIR, yaml


def _convert_image_to_ndarray(image_path: str, new_shape: tuple[int, int] = None) -> np.ndarray:
    image = imread(image_path, as_gray=True)
    if new_shape is not None and image.shape != new_shape:
        image = resize(image, new_shape)
    return image


def _compare_images(reference_image_array: np.ndarray, compare_image_array: np.ndarray) -> float:
    try:
        return structural_similarity(
            reference_image_array,
            compare_image_array,
            gaussian_weights=True,
            sigma=1.5,
            use_sample_covariance=False,
            data_range=1.0,
        )
    except Exception as err:
        logging.error("SSym Algorithm failed: %s", err)
        return -1


def _get_reference_tests():
    description_files = sorted(glob(DESCRIPTION_GLOB))

    reference_tests = {}

    for file_path in description_files:
        with open(file_path, "r", encoding="utf8") as yaml_file:
            content = yaml.load(yaml_file)
            for test_id, info in content.get("tests", {}).items():
                if info.get("type") == "Reference":
                    reference_tests[test_id] = info

    logging.debug("reference testcases are: %s", list(reference_tests.keys()))
    return reference_tests


def _get_reference_images(
    test_ids: str, reference_tests: dict, snapshots_dir: str, reference_screenshots_dir: str
):
    for test_id in test_ids:
        if test_id in reference_tests:
            image_paths = sorted(glob(join(snapshots_dir, test_id, "*.png")))
            if len(image_paths) == 0:
                continue
            # take the last screenshot as it has the highest probability to have the actual model
            # there take only one to reduce iterations of the compare algorithm.
            image_path = image_paths[-1]
            yield {
                "test_id": test_id,
                "test_name": reference_tests.get(test_id, {}).get("name"),
                "image": _convert_image_to_ndarray(image_path),
            }

    for image_path in sorted(glob(join(reference_screenshots_dir, "*.png"))):
        yield {
            "test_id": Path(image_path).stem,
            "test_name": "Manual reference screenshot",
            "image": _convert_image_to_ndarray(image_path),
        }


def _get_images_to_compare(test_ids: str, reference_tests: dict, snapshots_dir: str):
    for test_id in test_ids:
        if test_id in reference_tests:
            continue
        image_paths = sorted(glob(join(snapshots_dir, test_id, "*.png")))
        if len(image_paths) > 0:
            yield (test_id, image_paths[-1])


def _compare_worker(reference_images_cache: dict, input_queue: Queue, result_queue: Queue):
    logging.debug("Start compare worker")
    while True:

        reference_image_scoring = {}
        program_id, comp_img_id, comp_img_path = input_queue.get()

        for reference_image_id, reference_image_info in reference_images_cache.items():
            reference_image = reference_image_info["image"]
            similarity_score = _compare_images(
                reference_image,
                _convert_image_to_ndarray(comp_img_path, new_shape=reference_image.shape),
            )
            logging.debug(
                "%s | Compare %s to %s. Similarity: %s",
                program_id,
                comp_img_id,
                reference_image_id,
                similarity_score,
            )
            reference_image_scoring[reference_image_id] = similarity_score

        result_queue.put((program_id, comp_img_id, reference_image_scoring))
        logging.info("%s | %s compared against all reference images", program_id, comp_img_id)

        input_queue.task_done()


def _compare_to_reference_cases(program_id: str, test_ids: list[str], pool_size: int = 16) -> None:
    """Takes every testcase in test_ids compares them with the reference testcases
    (those need to be available in the snapshots directory as well).
    Given a certain similarity threshold the highest matching reference screenshot is linked to the
    info.yaml again. This is mainly to lessen the work needed to look at every single screenshot
    for the evaluation.
    """
    logging.info("%s | Start", program_id)

    _info_path = join(EVALUATION_DIR, program_id, "info.yaml")
    with open(_info_path, "r", encoding="utf8") as yaml_file:
        info_content = yaml.load(yaml_file)
        tests = info_content.get("tests", {})

    snapshots_dir = join(EVALUATION_DIR, program_id, "snapshots")
    reference_screenshots_dir = join(EVALUATION_DIR, program_id, "reference_screenshots")
    all_test_ids = [
        entry
        for entry in listdir(snapshots_dir)
        if isdir(join(snapshots_dir, entry)) and entry in tests
    ]

    reference_tests = _get_reference_tests()
    # hold the reference images in cache to not load them from disk every time
    reference_images_cache = {
        ref_img["test_id"]: {"image": ref_img["image"], "name": ref_img["test_name"]}
        for ref_img in _get_reference_images(
            all_test_ids, reference_tests, snapshots_dir, reference_screenshots_dir
        )
    }

    compare_image_queue = Manager().JoinableQueue()
    result_queue = Manager().Queue()

    original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    pool = Pool(processes=pool_size)
    signal.signal(signal.SIGINT, original_sigint_handler)
    try:
        pool.starmap_async(
            _compare_worker,
            [[reference_images_cache, compare_image_queue, result_queue]] * pool_size,
        )

        number_queued_items = 0

        for comp_test_id, comp_image_path in _get_images_to_compare(
            test_ids, reference_tests, snapshots_dir
        ):
            compare_image_queue.put((program_id, comp_test_id, comp_image_path))
            number_queued_items += 1

        compare_image_queue.join()
        logging.debug("%s | Compare workers done", program_id)
        for _ in range(number_queued_items):
            _, comp_test_id, reference_image_scoring = result_queue.get()

            heighest_scoring_ref_id = ("", -2)
            for reference_image_id, score in reference_image_scoring.items():
                if score > heighest_scoring_ref_id[1]:
                    heighest_scoring_ref_id = (reference_image_id, score)

            if heighest_scoring_ref_id[1] >= -1:
                tests[comp_test_id]["image_similarity"] = {
                    "similar_to": {
                        "test_id": heighest_scoring_ref_id[0],
                        "test_name": reference_images_cache[heighest_scoring_ref_id[0]]["name"],
                    },
                    "score": str(heighest_scoring_ref_id[1]),
                }
                logging.info(
                    "%s | %s is similar to %s (%s)",
                    program_id,
                    comp_test_id,
                    heighest_scoring_ref_id[0],
                    heighest_scoring_ref_id[1],
                )
        logging.debug("%s | Result gathering done", program_id)

        with open(_info_path, "w", encoding="utf8") as yaml_file:
            yaml.dump(info_content, yaml_file)

    except KeyboardInterrupt:
        logging.info("Caught KeyboardInterrupt, terminating sub-processes")
    finally:
        pool.terminate()
        pool.join()


def compare_screenshots(program_ids: list[str], test_ids: list[str]) -> None:
    """Compares all testcases of all given programs with the references cases.
    For more infos see: `_compare_to_reference_cases` function."""

    for program_id in program_ids:
        _compare_to_reference_cases(program_id, test_ids)
