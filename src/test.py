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
fh = logging.FileHandler(".log", mode="w")
fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)8s | %(name)s: %(message)s"))
fh.setLevel(logging.DEBUG)
logging.getLogger().addHandler(fh)


for program_cls in [
    # Chitubox,
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
    logging.info("============== Program %s ==============", program_cls().name)
    print()
    for test in parse_tests("R-HOU,R-ERR"):  # ,CS-0110,XML-MOD-ALT-OOB-R"):
        program: Program = program_cls()
        print()
        logging.info("======= Test %s =======", test)
        print()
        path = Path(r"C:\Users\jrossel\AppData\Local\Temp\3mftest", program.name, test.stem)
        path.mkdir(parents=True, exist_ok=True)
        try:
            for state, _time, screenshots in program.test(test, str(path.absolute())):
                print()
                logging.info("======= %s %s", state, _time)
                print()
                for screenshot in screenshots:
                    screenshot.write()
        except Exception as err:
            logging.exception("critical, something major broke")

    program.force_stop_all()

pass
