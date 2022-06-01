import logging
import sys
from os.path import join
from time import time
from typing import Dict, List, Tuple, Union

from matplotlib import pyplot
from mpl_toolkits import mplot3d
from stl import mesh

from .. import LIB3MF_DIR
from ..dataclasses import File, Program
from .run_tests import switch_server_logfile

sys.path.append(join(LIB3MF_DIR, "Bindings", "Python"))
import Lib3MF


def _to_stl(in_file_path: str, out_file_path: str):
    """Assumes in_file to be 3mf and out_file to be stl (and having those file types)."""
    wrapper = Lib3MF.Wrapper(join(LIB3MF_DIR, "Bin", "lib3mf"))

    model = wrapper.CreateModel()
    reader = model.QueryReader("3mf")
    reader.ReadFromFile(in_file_path)
    writer = model.QueryWriter("stl")
    writer.WriteToFile(out_file_path)


def _render_stl(stl_file_path: str, out_file_path: str):
    """Uses matplotlib to render the STL an saves it as PNG"""
    figure = pyplot.figure()
    axes = mplot3d.Axes3D(figure)

    your_mesh = mesh.Mesh.from_file(stl_file_path)
    mpl_collection = mplot3d.art3d.Poly3DCollection(your_mesh.vectors)
    mpl_collection.set_edgecolor("black")
    axes.add_collection3d(mpl_collection)

    scale = your_mesh.points.flatten()
    axes.auto_scale_xyz(scale, scale, scale)

    # Show the plot to the screen
    pyplot.savefig(out_file_path)


def stop(program: Program):
    pass


def test_program_on_file(
    program: Program,
    file: File,
    output_dir: str,
    **args,
) -> Union[None, Dict[str, Dict[str, str]]]:
    """Runs a program with the given file and creates screenshots of the result."""

    program_infos = {
        "company": "3MF Consortium",
        "version": "2.1.1",
        "product": "lib3mf",
    }

    switch_server_logfile(program, file, output_dir)

    output_filestem = "mesh"
    stl_file_path = join(output_dir, f"{output_filestem}.stl")
    png_file_path = join(output_dir, f"{output_filestem}.png")

    try:
        start_time = time()
        _to_stl(file.abspath, stl_file_path)
        execution_duration = time() - start_time
    except Exception as err:
        with open(join(output_dir, "error-info.txt"), "w", encoding="utf-8") as outfile:
            outfile.write(str(err))
        return program_infos

    with open(join(output_dir, "execution_duration.txt"), "w", encoding="utf-8") as outfile:
        outfile.write(str(execution_duration))

    try:
        _render_stl(stl_file_path, png_file_path)
    except Exception as err:
        logging.error(
            "Failed to render STL. %s: %s, %s\n%s",
            program.name,
            file.test_id,
            stl_file_path,
            err,
        )

    return program_infos
