"""Specific implementations of behavior for specific programs."""

import tempfile
from time import time

from appium.webdriver import Remote as RemoteDriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from ...dataclasses import File
from .base import AutomatedProgram, Capabilities, WinAppDriverProgram
from .utilclasses import ActionUnsuccessful, Be, By, Context, ExpectElement
from .utils import _run_ps_command, _try_action_until_timeout, sleep


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
                "program loaded": [ExpectElement(By.AUTOMATION_ID, "StartUpControlView")],
                "file loaded": [ExpectElement(By.AUTOMATION_ID, "Root3D")],
                "error": [ExpectElement(By.NAME, "OK")],
            },
        )

    def _pre_load_model(self):
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()
        sleep(2)

    def _post_wait_program_load(self):
        sleep(2)


class Tdviewer(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE, Capabilities.DETECT_CHANGE_SCREENSHOT],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "3dviewer",
            r"Microsoft.Microsoft3DViewer_8wekyb3d8bbwe!Microsoft.Microsoft3DViewer",
            "3DViewer",
            {
                "program loaded": [ExpectElement(By.AUTOMATION_ID, "WelcomeCloseButton")],
                "error": [ExpectElement(By.NAME, "Couldn't load 3D model")],
            },
        )
        self.tempdir = tempfile.mkdtemp()

    def _pre_load_model(self):
        self.driver.find_element(By.AUTOMATION_ID, "WelcomeCloseButton").click()
        sleep(2)

    def _wait_model_load(self, model: File, file_load_timeout: int):
        # wait until nothing changes any more (loaded model or hang) or error detected

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
                if not self._screen_changed() and not self._screen_changed():
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

        self.driver.find_element(By.AUTOMATION_ID, "SelectedAnimationText").click()
        self.driver.find_element(By.NAME, "Jump & Turn").click()

        def __callback():
            if self._screen_changed():
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


class Chitubox(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[
        Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE,
        Capabilities.DETECT_CHANGE_OCR,
        Capabilities.START_PROGRAM_LEGACY,
    ],
    additional_attributes={
        "open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL,
        "ocr_bounding_box": lambda self, left, upper, right, lower: (
            0,
            lower - (lower // 8),
            right // 2,
            lower,
        ),
        "window_title": "CHITUBOXPro",
        "window_load_timeout": 15,
    },
):
    def __init__(self) -> None:
        super().__init__(
            "chitubox",
            r"C:\Program Files\CHITUBOXPro V1.2.0\CHITUBOXPro.exe",
            "CHITUBOXPro",
            {
                "program starting": [
                    ExpectElement(
                        By.NAME,
                        "CHITUBOXPro",
                        parents=[
                            ExpectElement(By.NAME, "Desktop 1", context=Context.ROOT),
                        ],
                    )
                ],
                "program loaded": [ExpectElement(By.NAME, "Select")],
                "file loaded": [ExpectElement(By.XPATH, "//*[contains(@Name, '{name}')]")],
                "error": [ExpectElement(By.OCR, "Cann't open file")],
            },
        )

    def _post_wait_program_load(self):
        sleep(2)

    def _pre_load_model(self):
        try:
            updates_window: WebElement = self.driver.find_element(By.NAME, "Check For Updates")
            ActionChains(self.driver).move_to_element_with_offset(
                updates_window, 420, 5
            ).click().perform()
        except WebDriverException:
            pass
        else:
            sleep(1)
        element = self.driver.find_element(By.NAME, "CHITUBOX Pro V1.2.0")
        ActionChains(self.driver).move_to_element_with_offset(element, 0, 30).click().perform()
        sleep(2)
        ActionChains(self.driver).move_to_element_with_offset(element, 50, 150).click().perform()
        sleep(2)


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
#                 "program loaded": [(By.NAME, "Marketplace")],
#                 "file loaded": [(By.NAME, "Slice")],
#                 "error": [
#                     (By.NAME, "Unable to Open File"),
#                     (By.NAME, "No Models in File"),
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
            r"E:\Program Files\Ultimaker Cura 5.1.1\Ultimaker-Cura.exe",
            "Ultimaker-Cura",
            {
                "program loaded": [ExpectElement(By.NAME, "PREPARE")],
                "file loaded": [ExpectElement(By.NAME, "Slice")],
                "error": [
                    ExpectElement(By.NAME, "Unable to Open File"),
                    ExpectElement(By.NAME, "No Models in File"),
                ],
            },
        )

    def _post_stop(self):
        self.force_stop_all()


class FlashPrint(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "flashprint",
            r"C:\Users\jrossel\Desktop\programs\flashprint.lnk",
            "FlashPrint",
            {
                "program loaded": [ExpectElement(By.AUTOMATION_ID, "TitleBar")],
                "file loaded": [
                    ExpectElement(
                        By.NAME,
                        "Undo Ctrl+Z",
                        Be.AVAILABLE_ENABLED,
                        parents=[
                            ExpectElement(By.NAME, "Desktop 1", context=Context.ROOT),
                            ExpectElement(By.CLASS_NAME, "Qt5QWindowPopupDropShadowSaveBits"),
                        ],
                    )
                ],
                "error": [ExpectElement(By.NAME, "OK Enter")],
            },
        )

    def _pre_wait_model_load(self):
        self.driver.find_element(By.NAME, "Edit Alt+E").click()
        sleep(2)

    def _post_wait_model_load(self):
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()
        sleep(1)

    def _post_stop(self):
        # stop closes the winappdriver connection, but there is still a "save changes" dialogue
        self.force_stop_all()


class Fusion(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[
        Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE,
        Capabilities.START_PROGRAM_LEGACY,
        Capabilities.DETECT_CHANGE_OCR,
    ],
    additional_attributes={
        "open_file_dialogue_keys": Keys.CONTROL + "i" + Keys.CONTROL,
        "window_title": "Autodesk Fusion 360",
        "window_load_timeout": 20,
        "ocr_bounding_box": lambda self, left, upper, right, lower: (
            right // 2,
            lower // 2,
            right,
            lower,
        ),
    },
):
    """
    Program Changes: Set the keyboard shortcut CTRL+i to "Insert Mesh".
    """

    def __init__(self) -> None:
        super().__init__(
            "fusion",
            r"C:\Users\jrossel\AppData\Local\Autodesk\webdeploy"
            r"\production\6a0c9611291d45bb9226980209917c3d\FusionLauncher.exe",
            "Fusion*",
            {
                "program starting": [
                    ExpectElement(
                        By.AUTOMATION_ID,
                        "MW1",
                        Be.AVAILABLE,
                        parents=[
                            ExpectElement(By.NAME, "Desktop 1", context=Context.ROOT),
                        ],
                    )
                ],
                "program loaded": [ExpectElement(By.NAME, "BROWSER")],
                "file loaded": [ExpectElement(By.NAME, "INSERT MESH")],
                "error": [ExpectElement(By.OCR, "error")],
            },
        )

    def _wait_model_load(self, model: File, file_load_timeout: int):
        start = time()
        self.status_change_names["file loaded"] = [ExpectElement(By.NAME, "INSERT MESH")]
        super()._wait_model_load(model, file_load_timeout)
        end = time()
        self.status_change_names["file loaded"] = [
            ExpectElement(By.NAME, "OK", Be.AVAILABLE_ENABLED)
        ]
        super()._wait_model_load(model, int(file_load_timeout - (end - start)))

        # reset
        self.status_change_names["file loaded"] = [ExpectElement(By.NAME, "INSERT MESH")]

    def _post_stop(self):
        self.force_stop_all()


class IdeaMaker(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[
        Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE,
        Capabilities.DETECT_CHANGE_OCR,
        Capabilities.START_PROGRAM_LEGACY,
    ],
    additional_attributes={
        "open_file_dialogue_keys": Keys.CONTROL + "i" + Keys.CONTROL,
        "ocr_bounding_box": lambda self, left, upper, right, lower: (
            right // 3,
            lower // 3,
            right,
            lower,
        ),
        "window_title": "ideaMaker 4.2.3 (RAISE3D E2)",
        "window_load_timeout": 5,
    },
):
    def __init__(self) -> None:
        super().__init__(
            "ideamaker",
            r"E:\Program Files\Raise3D\ideaMaker\ideaMaker.exe",
            "ideaMaker",
            {
                "program loaded": [ExpectElement(By.NAME, "RaiseCloud")],
                "file loaded": [ExpectElement(By.NAME, "Move", Be.AVAILABLE_ENABLED)],
                "error": [ExpectElement(By.OCR, "invalid")],
            },
        )

    def _start_program(self):
        sleep(3)
        super()._start_program()


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
#                 # "program loaded": [(By.NAME, "RaiseCloud")],
#                 # "file loaded": [(By.NAME, "Move", Be.AVAILABLE_ENABLED)],
#                 # "error": [
#                 #     (By.NAME, "Load file failed {abspath}"),
#                 # ], TODO element to focusable (idea OCR?)
#             },
#             Keys.CONTROL + "o" + Keys.CONTROL,
#         )


class MeshMagic(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={
        "open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL,
    },
):
    def __init__(self) -> None:
        super().__init__(
            "meshmagic",
            r"C:\Users\jrossel\Desktop\programs\meshmagic.lnk",
            "meshmagic",
            {
                "program loaded": [
                    ExpectElement(By.NAME, "MeshMagic by NCH Software - Untitled.stl")
                ],
                "program loaded autosave": [ExpectElement(By.NAME, "Autosave")],
                "file loaded": [ExpectElement(By.NAME, "MeshMagic by NCH Software - {name}")],
                "error": [ExpectElement(By.NAME, "File Open Failed")],
            },
        )
        self.last_load_successful = None

    def _wait_program_load(self, model: File, program_start_timeout: int, retry=0):
        try:
            change_type = self._wait_for_change(
                names=self._transform_status_names(
                    ["program loaded", "program loaded autosave"],
                    self._get_format_strings(model),
                ),
                timeout=10,
            )
            if change_type == "program loaded autosave":
                self.driver.find_element(By.NAME, "OK").click()
                ActionChains(self.driver).send_keys(Keys.CONTROL + "n" + Keys.CONTROL).perform()
                ActionChains(self.driver).send_keys(Keys.CONTROL + "n" + Keys.CONTROL).perform()
                super()._wait_program_load(model, program_start_timeout)
        except ActionUnsuccessful as err:
            if retry > 2:
                raise err

            self.stop()
            self.force_stop_all()
            self._start_program()
            self._wait_program_load(model, program_start_timeout, retry=retry + 1)

    def _post_wait_model_load(self):
        # move the model so it is in view
        # ActionChains(self.driver).send_keys(Keys.CONTROL + "a" + Keys.CONTROL).perform()
        # ActionChains(self.driver).send_keys(Keys.CONTROL + "p" + Keys.CONTROL).perform()
        # for pos_elem in ["109", "111", "113"]:
        #     self.driver.find_element(By.NAME, pos_elem).click()
        #     ActionChains(self.driver).send_keys("0" + Keys.ENTER + Keys.ENTER).perform()
        # for scale_elem in ["127", "129", "131"]:
        #     self.driver.find_element(By.NAME, scale_elem).click()
        #     ActionChains(self.driver).send_keys("0.1" + Keys.ENTER + Keys.ENTER).perform()
        # self.driver.find_element(By.NAME, "Accept").click()
        self._focus_window()
        ActionChains(self.driver).send_keys(*[Keys.END + Keys.END] * 10).perform()

    def _post_model_load_success(self):
        # discard the changes to the model
        # otherwise it is loaded the next time meshmagic is started
        # ActionChains(self.driver).send_keys(Keys.CONTROL + "zzz" + Keys.CONTROL).perform()
        # ActionChains(self.driver).send_keys(Keys.CONTROL + "zzz" + Keys.CONTROL).perform()
        self.last_load_successful = True

    def _post_model_load_failure(self):
        self.last_load_successful = False

    # def _pre_stop(self):
    #     ActionChains(self.driver).send_keys(Keys.ALT + Keys.F4 + Keys.ALT).perform()

    def _post_stop(self):
        if self.last_load_successful:
            return

        self.force_stop_all()
        sleep(2)
        _run_ps_command(["Start-Process", "-FilePath", self.executable_path])
        sleep(10)
        self.force_stop_all()


class MeshMixer(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.DETECT_CHANGE_OCR],
    additional_attributes={
        "ocr_bounding_box": lambda self, left, upper, right, lower: (
            right // 4,
            lower // 4,
            (right // 4) * 3,
            (lower // 4) * 3,
        ),
    },
):
    def __init__(self) -> None:
        super().__init__(
            "meshmixer",
            r"C:\Users\jrossel\Desktop\programs\meshmixer.lnk",
            "meshmixer",
            {
                "program loaded": [ExpectElement(By.NAME, "Autodesk Meshmixer")],
                "file loading": [ExpectElement(By.OCR, "computing...", Be.NOTAVAILABLE)],
                "file loaded": [ExpectElement(By.NAME, "Autodesk Meshmixer - {name}")],
                "error": [ExpectElement(By.NAME, "Error opening file :")],
            },
        )

    def _post_wait_program_load(self):
        try:
            self._wait_for_change(
                names={"recovery": [ExpectElement(By.NAME, "Don't Restore")]},
                timeout=5,
            )
            self.driver.find_element(By.NAME, "Don't Restore").click()
        except (WebDriverException, ActionUnsuccessful):
            pass

    def _load_model(self, model: File):
        self.driver.find_element(By.NAME, "Import").click()
        sleep(2)
        self.driver.find_element_by_name("File name:").click()
        ActionChains(self.driver).send_keys(model.abspath).perform()
        ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()

    def _wait_model_load(self, model: File, file_load_timeout: int):
        self._wait_for_change(
            names=self._transform_status_names(
                ["file loading"],
                self._get_format_strings(model),
            ),
            timeout=file_load_timeout,
        )
        super()._wait_model_load(model, file_load_timeout)

    def _post_stop(self):
        self.force_stop_all()


class Office(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={
        "open_file_dialogue_keys": Keys.ALT + Keys.ALT + "n" + "s3" + "d",
    },
):
    def __init__(self) -> None:
        super().__init__(
            "office",
            r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            "POWERPNT",
            {
                "program loaded": [ExpectElement(By.NAME, "PowerPoint")],
                "file loaded": [ExpectElement(By.NAME, "3D Model")],
                "error": [
                    ExpectElement(
                        By.XPATH,
                        "//*[contains(@Name, 'An error occurred while importing this file')]",
                    )
                ],
            },
        )

    def _start_program(self):
        self.driver = RemoteDriver(
            command_executor="http://127.0.0.1:4723",
            desired_capabilities={
                "app": self.executable_path,
                "appArguments": "/s",
            },
        )

    def _pre_load_model(self):
        """Open empty slide set"""
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()


class Paint3d(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
):
    def __init__(self) -> None:
        super().__init__(
            "paint3d",
            r"Microsoft.MSPaint_8wekyb3d8bbwe!Microsoft.MSPaint",
            "PaintStudio.View",
            {
                "program loaded": [ExpectElement(By.NAME, "Show welcome screen")],
                "file loaded": [ExpectElement(By.NAME, "Undo", Be.AVAILABLE_ENABLED)],
                "error": [
                    ExpectElement(By.NAME, "Couldn't import model"),
                    ExpectElement(By.NAME, "Paint 3D needs to close"),
                ],
            },
        )

    def _pre_load_model(self):
        ActionChains(self.driver).send_keys(
            Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE + Keys.ESCAPE
        ).perform()
        sleep(2)

    def _load_model(self, model: File):
        ActionChains(self.driver).send_keys(Keys.ALT + "f" + Keys.ALT).perform()
        sleep(1)
        ActionChains(self.driver).send_keys(Keys.ALT + "i" + Keys.ALT).perform()
        sleep(2)
        self.driver.find_element_by_name("File name:").click()
        ActionChains(self.driver).send_keys(model.abspath).perform()
        ActionChains(self.driver).send_keys(Keys.ALT + "o" + Keys.ALT).perform()

    def _post_stop(self):
        self.force_stop_all()


class Prusa(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "prusa",
            r"C:\Users\jrossel\Desktop\programs\prusa.lnk",
            "prusa-slicer",
            {
                "program loaded": [ExpectElement(By.NAME, "GLCanvas")],
                "file loaded": [ExpectElement(By.NAME, "{stem}")],
                "question asked": [ExpectElement(By.NAME, "Multi-part object detected")],
                "error": [ExpectElement(By.NAME, "PrusaSlicer error")],
            },
        )

    def _wait_model_load(self, model: File, file_load_timeout: int):
        change_type = self._wait_for_change(
            names=self._transform_status_names(
                ["error", "file loaded", "question asked"],
                self._get_format_strings(model),
            ),
            timeout=file_load_timeout,
        )
        if change_type == "question asked":
            element = self._wait_for_change(
                names=self._transform_status_names(
                    ["question asked"],
                    self._get_format_strings(model),
                ),
                timeout=file_load_timeout,
                return_change_type=False,
            )
            ActionChains(self.driver).click(on_element=element).perform()
            ActionChains(self.driver).send_keys(Keys.ALT + "y" + Keys.ALT).perform()
            ActionChains(self.driver).send_keys(Keys.ALT + "y" + Keys.ALT).perform()
            super()._wait_model_load(model, file_load_timeout)


class Simplify(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "i" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "simplify",
            r"C:\Users\jrossel\Desktop\programs\simplify.lnk",
            "Simplify3D",
            {
                "program loaded": [ExpectElement(By.NAME, "Prepare to Print!")],
                "file loaded": [ExpectElement(By.NAME, "{stem}")],
                "error": [
                    ExpectElement(By.XPATH, "//*[contains(@Name, 'Error parsing 3MF file')]")
                ],
            },
        )


class Slic3r(
    WinAppDriverProgram,
    metaclass=AutomatedProgram,
    capabilities=[Capabilities.OPEN_MODEL_VIA_FILE_DIALOGUE],
    additional_attributes={"open_file_dialogue_keys": Keys.CONTROL + "o" + Keys.CONTROL},
):
    def __init__(self) -> None:
        super().__init__(
            "slic3r",
            r"C:\Users\jrossel\Desktop\programs\slic3r.lnk",
            "Slic3r",
            {
                "program loaded": [ExpectElement(By.NAME, "Add…")],
                "file loaded": [
                    ExpectElement(By.NAME, "Loaded {name}"),
                    ExpectElement(
                        By.NAME,
                        "Some of your object(s) appear to be outside the print bed. "
                        "Use the arrange button to correct this.",
                    ),
                ],
                "error": [ExpectElement(By.NAME, "Error")],
            },
        )


class SuperSlicer(Prusa):
    def __init__(self) -> None:
        super().__init__()
        self.name = "superslicer"
        self.executable_path = r"C:\Users\jrossel\Desktop\programs\superslicer.lnk"
        self.process_name = "superslicer"
        self.status_change_names["error"] = [ExpectElement(By.NAME, "SuperSlicer error")]
