import logging
import shutil
import tempfile
from pathlib import Path
from time import sleep

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from threemf_analyzer.dataclasses import DiskFile, File
from threemf_analyzer.evaluate.screenshots import _compare_images, _convert_image_to_ndarray
from threemf_analyzer.run.programs.base import (
    ActionUnsuccessful,
    AutomatedProgram,
    Be,
    Capabilities,
    WinAppDriverProgram,
    _try_action_until_timeout,
)
from threemf_analyzer.utils import parse_tests

logging.getLogger().setLevel("DEBUG")


class Tdbuilder(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "l" + Keys.CONTROL},
):
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

    def _pre_load_model(self):
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()
        sleep(2)


class Tdviewer(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "3dviewer",
            r"Microsoft.Microsoft3DViewer_8wekyb3d8bbwe!Microsoft.Microsoft3DViewer",
            "3DViewer",
            {
                "program loaded": [("accessibility id", "WelcomeCloseButton", Be.AVAILABLE)],
                "error": [(By.NAME, "Couldn't load 3D model", Be.AVAILABLE)],
            },
        )
        self.tempdir = tempfile.mkdtemp()

    def _pre_load_model(self):
        self.driver.find_element("accessibility id", "WelcomeCloseButton").click()
        sleep(2)

    def _wait_model_load(self, model: File, file_load_timeout: int):
        # wait until nothing changes any more (loaded model or hang) or error detected
        last_screenshot_path = str(Path(self.tempdir, "last.png").resolve())
        current_screenshot_path = str(Path(self.tempdir, "current.png"))
        self.driver.save_screenshot(last_screenshot_path)

        sleep(2)

        def __screen_changed():
            """Checks if the screen updated."""
            self.driver.save_screenshot(current_screenshot_path)
            score = _compare_images(
                _convert_image_to_ndarray(last_screenshot_path),
                _convert_image_to_ndarray(current_screenshot_path),
            )
            shutil.copyfile(current_screenshot_path, last_screenshot_path)
            logging.debug("Screenshots compared to: %s", score)
            return score < 0.99999

        def __callback():
            try:
                return self._find_elements(
                    self._transform_status_names(
                        ["error"],
                        {
                            "abspath": model.abspath,
                            "name": model.name,
                            "stem": model.stem,
                        },
                    )
                )
            except WebDriverException:
                if not __screen_changed() and not __screen_changed():
                    return "screen not changed"
            raise ActionUnsuccessful("screen still changes and no error detected")

        change_type = _try_action_until_timeout(
            "detect no change or error",
            __callback,
            file_load_timeout,
            (ActionUnsuccessful,),
            rate=1,
        )
        if change_type == "error":
            raise ActionUnsuccessful("error msg detected in window")

        self.driver.find_element("accessibility id", "SelectedAnimationText").click()
        self.driver.find_element(By.NAME, "Jump & Turn").click()

        def __callback():
            if __screen_changed():
                return
            try:
                self._find_elements(
                    self._transform_status_names(
                        ["error"],
                        {
                            "abspath": model.abspath,
                            "name": model.name,
                            "stem": model.stem,
                        },
                    )
                )
                return
            except WebDriverException:
                pass
            raise ActionUnsuccessful("screen frozen and no error detected")

        _try_action_until_timeout(
            "detect change", __callback, file_load_timeout, (ActionUnsuccessful,), rate=1
        )


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


class Cura(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
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
        )


# test if object loaded via undo button
class FlashPrint(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "i" + Keys.CONTROL},
):
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
class Fusion(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "i" + Keys.CONTROL},
):
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


class IdeaMaker(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
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


for program_cls in [Tdviewer]:
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
