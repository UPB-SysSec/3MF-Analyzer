import logging
from pathlib import Path
from time import sleep

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from threemf_analyzer.dataclasses import DiskFile, File
from threemf_analyzer.run.programs.base import (
    ActionUnsuccessful,
    Be,
    DefaultWinAppDriverProgram,
    WinAppDriverProgram,
)
from threemf_analyzer.utils import parse_tests

logging.getLogger().setLevel("DEBUG")


class Tdbuilder(WinAppDriverProgram):
    def __init__(self) -> None:
        super().__init__(
            "3dbuilder",
            r"Microsoft.3DBuilder_8wekyb3d8bbwe!App",
            "Builder3D",
            {
                "program loaded": [("accessibility id", "StartUpControlView", Be.AVAILABLE)],
                "file loaded": [("accessibility id", "Root3D", Be.AVAILABLE)],
                "error": [(By.NAME, "OK", Be.AVAILABLE)],
            },
        )

    def _load_model(self, model: File):
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()
        sleep(2)
        ActionChains(self.driver).send_keys(Keys.CONTROL + "l" + Keys.CONTROL).perform()
        sleep(2)
        self.driver.find_element_by_name("File name:").click()
        ActionChains(self.driver).send_keys(model.abspath).perform()
        ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()


class Tdviewer(WinAppDriverProgram):
    def __init__(self) -> None:
        super().__init__(
            "3dviewer",
            r"Microsoft.Microsoft3DViewer_8wekyb3d8bbwe!Microsoft.Microsoft3DViewer",
            "3DViewer",
            {
                "program loaded": [("accessibility id", "WelcomeCloseButton", Be.AVAILABLE)],
                "file loaded": [
                    ("accessibility id", "PlayPauseButton", Be.NOTAVAILABLE)
                ],  # TODO no element changes once the model is loaded, not sure what we can do here.
                "error": [(By.NAME, "Couldn't load 3D model", Be.AVAILABLE)],
            },
        )

    def _load_model(self, model: File):
        self.driver.find_element_by_name("Close").click()
        sleep(2)
        ActionChains(self.driver).send_keys(Keys.CONTROL + "o" + Keys.CONTROL).perform()
        sleep(2)
        self.driver.find_element_by_name("File name:").click()
        ActionChains(self.driver).send_keys(model.abspath).perform()
        ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()


#########
# Does not start on VM... (no OpenGL 4 support, only 3.3)
#########
# class Craftware(WinAppDriverProgram):
#     def __init__(self) -> None:
#         super().__init__(
#             "craftware",
#             # r"E:\Program Files\Ultimaker Cura 5.1.1\Ultimaker-Cura.exe",
#             r"C:\Program Files\Craftunique\CraftWare Pro\bin\craftApp.exe",
#             "Ultimaker-Cura",
#             {
#                 "program loaded": [(By.NAME, "Marketplace", Be.AVAILABLE)],
#                 "file loaded": [(By.NAME, "Slice", Be.AVAILABLE)],
#                 "error": [
#                     (By.NAME, "Unable to Open File", Be.AVAILABLE),
#                     (By.NAME, "No Models in File", Be.AVAILABLE),
#                 ],
#             },
#         )

#     def _load_model(self, model: File):
#         ActionChains(self.driver).send_keys(Keys.CONTROL + "o" + Keys.CONTROL).perform()
#         sleep(2)
#         self.driver.find_element_by_name("File name:").click()
#         ActionChains(self.driver).send_keys(model.abspath).perform()
#         ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()


class Cura(DefaultWinAppDriverProgram):
    def __init__(self) -> None:
        super().__init__(
            "cura",
            # r"E:\Program Files\Ultimaker Cura 5.1.1\Ultimaker-Cura.exe",
            r"C:\Users\jrossel\Desktop\programs\cura.lnk",
            "Ultimaker-Cura",
            {
                "program loaded": [(By.NAME, "Marketplace", Be.AVAILABLE)],
                "file loaded": [(By.NAME, "Slice", Be.AVAILABLE)],
                "error": [
                    (By.NAME, "Unable to Open File", Be.AVAILABLE),
                    (By.NAME, "No Models in File", Be.AVAILABLE),
                ],
            },
            Keys.CONTROL + "o" + Keys.CONTROL,
        )


# test if object loaded via undo button
class FlashPrint(DefaultWinAppDriverProgram):
    def __init__(self) -> None:
        super().__init__(
            "flashprint",
            r"C:\Users\jrossel\Desktop\programs\flashprint.lnk",
            "FlashPrint",
            {
                "program loaded": [("accessibility id", "TitleBar", Be.AVAILABLE)],
                # "file loaded": [(By.NAME, "Slice", Be.AVAILABLE)], TODO
                "error": [(By.NAME, "Load file failed {abspath}", Be.AVAILABLE)],
            },
            Keys.CONTROL + "i" + Keys.CONTROL,
        )


# use save state for detection
class Fusion(DefaultWinAppDriverProgram):
    """
    Problems: file loaded sometimes pops up before the model is loaded.
    Program Changes: Set the keyboard shortcut CTRL+i to "Insert Mesh".
    """

    def __init__(self) -> None:
        super().__init__(
            "fusion",
            r"C:\Users\jrossel\Desktop\programs\fusion.lnk",
            "Fusion*",
            {
                "program loaded": [(By.NAME, "BROWSER", Be.AVAILABLE)],
                "file loaded": [(By.NAME, "INSERT MESH", Be.AVAILABLE)],
                # "error": [
                #     (By.NAME, "Load file failed {abspath}", Be.AVAILABLE),
                # ], TODO element to focusable (idea OCR?)
            },
            Keys.CONTROL + "i" + Keys.CONTROL,
        )

    def _wait_model_load(self, model: File, file_load_timeout: int):
        """Busy-wait for the model to load.
        ActionUnsuccessful is raised if the model cannot be loaded."""
        start = time()
        self.status_change_names["file loaded"] = [(By.NAME, "INSERT MESH", Be.AVAILABLE)]
        super()._wait_model_load(model, file_load_timeout)
        end = time()
        self.status_change_names["file loaded"] = [(By.NAME, "Ok", Be.AVAILABLE_ENABLED)]
        super()._wait_model_load(model, int(file_load_timeout - (end - start)))

        # reset
        self.status_change_names["file loaded"] = [(By.NAME, "INSERT MESH", Be.AVAILABLE)]


class IdeaMaker(WinAppDriverProgram):
    def __init__(self) -> None:
        super().__init__(
            "ideamaker",
            r"C:\Users\jrossel\Desktop\programs\ideamaker.lnk",
            "ideaMaker",
            {
                "program loaded": [(By.NAME, "RaiseCloud", Be.AVAILABLE)],
                "file loaded": [(By.NAME, "Move", Be.AVAILABLE_ENABLED)],
                # "error": [
                #     (By.NAME, "Load file failed {abspath}", Be.AVAILABLE),
                # ], TODO element to focusable (idea OCR?)
            },
            Keys.CONTROL + "o" + Keys.CONTROL,
        )


#########
# Does not start on VM... (prob. OpenGL version)
#########
# class Lychee(WinAppDriverProgram):
#     def __init__(self) -> None:
#         super().__init__(
#             "lychee",
#             r"C:\Users\jrossel\Desktop\programs\lychee.lnk",
#             "LycheeSlicer",
#             {
#                 # "program loaded": [(By.NAME, "RaiseCloud", Be.AVAILABLE)],
#                 # "file loaded": [(By.NAME, "Move", Be.AVAILABLE_ENABLED)],
#                 # "error": [
#                 #     (By.NAME, "Load file failed {abspath}", Be.AVAILABLE),
#                 # ], TODO element to focusable (idea OCR?)
#             },
#             Keys.CONTROL + "o" + Keys.CONTROL,
#         )


for program_cls in [Cura]:
    program = program_cls()
    for test in parse_tests("R-HOU,R-ERR"):
        print(f"============== Test {test} ==============")
        path = Path(r"C:\Users\jrossel\AppData\Local\Temp\3mftest", program.name, test.stem)
        path.mkdir(parents=True, exist_ok=True)
        for state, time, screenshots in program.test(test, str(path.absolute())):
            print("=======", state, time)
            screenshot: DiskFile
            for screenshot in screenshots:
                screenshot.write()

pass
