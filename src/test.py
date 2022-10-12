import logging
from pathlib import Path

from threemf_analyzer.run.programs.base import Program
from threemf_analyzer.run.programs.programs import (
    Chitubox,
    Cura,
    FlashPrint,
    Fusion,
    IdeaMaker,
    MeshMagic,
    MeshMixer,
    Office,
    Paint3d,
    Prusa,
    Simplify,
    Slic3r,
    SuperSlicer,
    Tdbuilder,
    Tdviewer,
)
from threemf_analyzer.utils import parse_tests

logging.getLogger().setLevel("DEBUG")

for program_cls in [
    Chitubox,
    # Office,
    # Tdbuilder,
    # Tdviewer,
    # Cura,
    # FlashPrint,
    # Fusion,
    # IdeaMaker,
    # MeshMagic,
    # MeshMixer,
    # Paint3d,
    # Prusa,
    # Simplify,
    # Slic3r,
    # SuperSlicer,
]:
    print()
    print(f"============== Program {program_cls().name} ==============")
    print()
    for test in parse_tests("R-HOU,R-ERR"):  # ,CS-0110,XML-MOD-ALT-OOB-R"):
        program: Program = program_cls()
        print()
        print(f"======= Test {test} =======")
        print()
        path = Path(r"C:\Users\jrossel\AppData\Local\Temp\3mftest", program.name, test.stem)
        path.mkdir(parents=True, exist_ok=True)
        for state, _time, screenshots in program.test(test, str(path.absolute())):
            print()
            print("=======", state, _time)
            print()
            for screenshot in screenshots:
                screenshot.write()

    program.force_stop_all()

pass
