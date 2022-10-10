from pathlib import Path

from threemf_analyzer.run.programs.programs import (
    Cura,
    FlashPrint,
    Fusion,
    IdeaMaker,
    MeshMagic,
    MeshMixer,
    Paint3d,
    Prusa,
    Simplify,
    Slic3r,
    SuperSlicer,
    Tdbuilder,
    Tdviewer,
)
from threemf_analyzer.utils import parse_tests

for program_cls in [
    # Tdbuilder,
    # Tdviewer,
    # Cura,
    # FlashPrint,
    # Fusion,
    IdeaMaker,
    MeshMagic,
    MeshMixer,
    Paint3d,
    Prusa,
    Simplify,
    Slic3r,
    SuperSlicer,
]:
    program = program_cls()
    for test in parse_tests("R-HOU,R-ERR,CS-0110,XML-MOD-ALT-OOB-R"):
        print()
        print(f"=============================== Test {test} ===============================")
        print()
        path = Path(r"C:\Users\jrossel\AppData\Local\Temp\3mftest", program.name, test.stem)
        path.mkdir(parents=True, exist_ok=True)
        for state, _time, screenshots in program.test(test, str(path.absolute())):
            print()
            print("=======", state, _time)
            print()
            for screenshot in screenshots:
                screenshot.write()

pass
