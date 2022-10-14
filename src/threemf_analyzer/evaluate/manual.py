"""Provides a simple GUI to manually evaluate test cases."""

import logging
from copy import deepcopy
from functools import lru_cache
from glob import glob
from io import StringIO
from os.path import join
from pathlib import Path
from typing import Any, Callable

from PIL import Image, ImageTk

from .. import EVALUATION_DIR, yaml
from ..utils import get_all_tests

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    tk = None
    logging.error(
        "Cannot import tkinter. Is tk correctly installed?\nManual evaluation not possible."
    )


STATE = {
    "current_program_index": 0,
    "current_test_index": 0,
}


class Switcher:
    """Simple iterator that can give the previous or the next item."""

    def __init__(self, name: str, items: list[Any], start_at: int = 0) -> None:
        self.name = name
        self.items = items
        self.index = start_at
        if start_at == -1:
            self.index = len(self.items) - 1
        self.buttons = None

    def get_buttons(self, frame: tk.Frame, callback: Callable):
        self.buttons = [
            tk.Button(
                frame,
                text=f"< Prev {self.name}",
                command=lambda: callback(self.prev),
            ),
            tk.Button(
                frame,
                text=f"Next {self.name} >",
                command=lambda: callback(self.next),
            ),
        ]
        self.buttons[0]["state"] = tk.NORMAL
        self.buttons[1]["state"] = tk.NORMAL
        if self.index == 0:
            self.buttons[0]["state"] = tk.DISABLED
        if self.index == len(self.items) - 1:
            self.buttons[1]["state"] = tk.DISABLED
        callback(self.curr)

        return self.buttons

    def prev(self) -> Any:
        """Returns the previous item. If there isn't one, return None and show info box."""
        self.index -= 1
        self.buttons[0]["state"] = tk.NORMAL
        self.buttons[1]["state"] = tk.NORMAL
        if self.index == 0:
            self.buttons[0]["state"] = tk.DISABLED
        if self.index < 0:
            messagebox.showinfo(title="End", message=f"No more {self.name}s")
            self.index += 1
            return
        return self.items[self.index]

    def curr(self) -> Any:
        return self.items[self.index]

    def next(self) -> Any:
        """Returns the next item. If there isn't one, return None and show info box."""
        self.index += 1
        self.buttons[0]["state"] = tk.NORMAL
        self.buttons[1]["state"] = tk.NORMAL
        if self.index == len(self.items) - 1:
            self.buttons[1]["state"] = tk.DISABLED
        if self.index > len(self.items) - 1:
            self.index -= 1
            messagebox.showinfo(title="End", message=f"No more {self.name}s")
            return
        return self.items[self.index]


class SimpleCache:
    def __init__(self, user_function, maxsize) -> None:
        self.func = user_function
        self.maxsize = maxsize
        self.cache = {}

    def __call__(self, *args):
        if args in self.cache:
            # move entry to end of dict
            res = self.cache.pop(args)
            self.cache[args] = res
            return res
        result = self.func(*args)
        self.cache[args] = result
        if len(self.cache) > self.maxsize:
            for key in self.cache.keys():
                self.cache.pop(key)
                if len(self.cache) <= self.maxsize:
                    break
        return result

    def invalidate(self, *args):
        if args in self.cache:
            del self.cache[args]


def _to_yaml_str(obj):
    with StringIO() as res:
        yaml.dump(obj, res)
        return res.getvalue()


def _from_yaml_str(_str):
    return yaml.load(StringIO(_str))


def _make_info_text(root, _str):
    root.update()
    res = tk.Text(
        root,
        # text=_str,
        # justify=tk.LEFT,
        width=80,
        height=len(_str.split("\n")),
        # font="TkFixedFont",
        # wraplength=root.winfo_reqwidth(),
        bg="#d9d9d9",
        bd=0,
        highlightthickness=0,
    )
    res.insert("1.0", _str)
    res.configure(state="disabled")
    return res


def _make_edit_field(root, name, init_data="", size=(70, 1)):
    frame = tk.Frame(root)
    label = tk.Label(
        frame,
        text=name,
        justify=tk.LEFT,
        width=10,
        font="TkFixedFont",
    )
    label.pack(side=tk.LEFT)
    field = tk.Text(frame, width=size[0], height=size[1])
    field.insert("1.0", init_data)
    field.pack(side=tk.LEFT)
    return frame, label, field


@lru_cache(maxsize=25)
def _get_all_screenshots(program_id, test_id, max_width, max_height):
    """Loads and resizes all given screenshots"""
    image_paths = sorted(glob(join(EVALUATION_DIR, program_id, "snapshots", test_id, "*.png")))
    all_screenshots = []
    for path in image_paths:
        image = Image.open(path)
        if max_width > 1 and max_height > 1:
            ratio = min(max_width / image.width, max_height / image.height)
            image = image.resize((int(image.width * ratio), int(image.height * ratio)))
        all_screenshots.append((ImageTk.PhotoImage(image), Path(path).name.replace(".png", "")))
    if not image_paths:
        all_screenshots.append(("", "No images"))
    return all_screenshots


def __get_eval_info(info_yaml_path) -> str:
    with open(info_yaml_path, encoding="utf-8") as yaml_file:
        content = yaml.load(yaml_file)
    return content


_get_eval_info = SimpleCache(__get_eval_info, 100)


def _display_test(
    root: tk.Tk,
    button_frame: tk.Frame,
    program_id: str,
    test_id: str,
    all_tests: dict,
) -> None:
    """"""
    root.title(f"{program_id} - {test_id}")

    info_yaml_path = join(EVALUATION_DIR, program_id, "info.yaml")
    test_infos = all_tests.get(test_id, "")

    for widget in root.grid_slaves():
        # if widget.widgetName == "screenshot":
        widget.grid_forget()

    # determine window size
    root.update()
    _width = root.winfo_width()
    _height = root.winfo_height()

    all_screenshots = _get_all_screenshots(
        program_id, test_id, int(_width * 0.75), int(_height * 0.75)
    )
    logging.debug(_get_all_screenshots.cache_info())

    # defines screenshot label, the function and button to switch
    screenshot_label = tk.Label(root, compound=tk.TOP, name="screenshot")

    def set_image(switcher_function):
        """Callback function of screenshot switching button"""
        item = switcher_function()
        screenshot_label["text"] = "No Image"

        if item is not None:
            image, caption = item
            screenshot_label["text"] = caption
            screenshot_label["image"] = image

    picture_switcher = Switcher("Screenshot", all_screenshots, start_at=-1)
    btn_frame = tk.Frame(root)
    btns = picture_switcher.get_buttons(btn_frame, set_image)
    for btn in btns:
        btn.pack(side=tk.LEFT)

    content = _get_eval_info(info_yaml_path)
    eval_test_infos = content.get("tests", {}).get(test_id)
    all_alerts = content.get("alerts", {})

    # defines information fields besides the screenshot
    infos_frame = tk.Frame(root)

    alert_infos = tk.Text(infos_frame, width=80, height=20)
    alert_infos.insert("1.0", _to_yaml_str(all_alerts))

    edit_fields = {
        name: _make_edit_field(
            infos_frame, name, init_data=eval_test_infos.get(name, ""), size=size
        )
        for name, size in [
            ("status", (70, 1)),
            ("alert", (70, 1)),
            ("info", (70, 15)),
            ("rerun", (70, 1)),
        ]
    }

    # just so it exists already
    infos = {}

    def update_alerts():
        """Callback of alerts update button"""
        try:
            content = _get_eval_info(info_yaml_path)
            new = infos["alert_infos"].get("1.0", tk.END).strip()
            new = _from_yaml_str(new)
            content["alerts"] = new
            with open(info_yaml_path, "w", encoding="utf-8") as yaml_file:
                yaml.dump(content, yaml_file)
                _get_eval_info.invalidate(info_yaml_path)
            infos["alert_infos"].replace("1.0", tk.END, _to_yaml_str(new))
        except Exception as err:
            messagebox.showerror(title="Error", message=err)

    def fill_info_fields():
        """Fills the info fields with the current data."""
        try:
            content = _get_eval_info(info_yaml_path)
            auto_eval_test_infos = deepcopy(content["tests"][test_id])
            for name in edit_fields:
                auto_eval_test_infos.pop(name, None)
            infos["eval_infos"] = _make_info_text(
                infos_frame, f"\n{_to_yaml_str(auto_eval_test_infos)}\n"
            )
            for name, (_, _, field) in edit_fields.items():
                field.replace("1.0", tk.END, eval_test_infos.get(name, ""))

        except Exception as err:
            messagebox.showerror(title="Error", message=err)

    def update_infos():
        """Callback of info update button"""
        try:
            content = _get_eval_info(info_yaml_path)
            for name, (_, _, field) in edit_fields.items():
                new = field.get("1.0", tk.END).strip()
                if new != "":
                    if new in ("True", "False", 1, 0, "true", "false", "t", "f"):
                        content["tests"][test_id][name] = new in ("t", "true", "True", 1)
                    else:
                        content["tests"][test_id][name] = new
                else:
                    content["tests"][test_id].pop(name, None)
            with open(info_yaml_path, "w", encoding="utf-8") as yaml_file:
                yaml.dump(content, yaml_file)
                _get_eval_info.invalidate(info_yaml_path)
            fill_info_fields()
        except Exception as err:
            messagebox.showerror(title="Error", message=err)

    # def save():
    #     """Does both update_alerts and update_infos, but less redundant"""
    #     try:
    #         content = _get_eval_info(info_yaml_path)
    #         for name, (_, _, field) in edit_fields.items():
    #             new = field.get("1.0", tk.END).strip()
    #             if new != "":
    #                 content["tests"][test_id][name] = new
    #         new = infos["alert_infos"].get("1.0", tk.END).strip()
    #         new = _from_yaml_str(new)
    #         content["alerts"] = new
    #         with open(info_yaml_path, "w", encoding="utf-8") as yaml_file:
    #             yaml.dump(content, yaml_file)
    #             _get_eval_info.invalidate(info_yaml_path)
    #         fill_info_fields()
    #         infos["alert_infos"].replace("1.0", tk.END, _to_yaml_str(new))
    #     except Exception as err:
    #         messagebox.showerror(title="Error", message=err)

    # remember the widgets and organize them on the grid
    infos = {
        "title": _make_info_text(infos_frame, f"{program_id} - {test_id}\n\n"),
        "test_infos": _make_info_text(infos_frame, _to_yaml_str(test_infos)),
        "alert_title": _make_info_text(infos_frame, "Defined Alerts"),
        "alert_infos": alert_infos,
        "alert_button": tk.Button(
            infos_frame,
            text="Update Alerts YAML",
            command=update_alerts,
        ),
        "eval_title": _make_info_text(infos_frame, "\n\nAutomatic Eval Results"),
        "eval_infos": "",
        "status": edit_fields["status"][0],
        "info": edit_fields["info"][0],
        "alert": edit_fields["alert"][0],
        "rerun": edit_fields["rerun"][0],
        "info_button": tk.Button(
            infos_frame,
            text="Update Infos",
            command=update_infos,
        ),
    }
    fill_info_fields()
    for index, (_, widget) in enumerate(infos.items()):
        widget.grid(column=0, row=index, sticky=tk.W)

    screenshot_label.grid(column=0, row=0)
    infos_frame.grid(column=1, row=0, sticky=tk.W)
    btn_frame.grid(column=0, row=1, sticky=tk.S, columnspan=2)
    button_frame.grid(column=0, row=2, sticky=tk.S, columnspan=2)
    root.rowconfigure(0, weight=10000)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=10000)

    # root.bind("<Control-s>", lambda _: save())


def show_screenshots(program_ids: list[str], test_ids: list[str]) -> None:
    if tk is None:
        return

    all_tests = get_all_tests()
    root = tk.Tk()

    program_switcher = Switcher("Program", program_ids)
    test_switcher = Switcher("Test", test_ids)

    def _update_test_view(switcher_function):
        item = switcher_function()
        if item is not None:
            _display_test(
                root,
                btn_frame,
                program_switcher.curr(),
                test_switcher.curr(),
                all_tests,
            )

    btn_frame = tk.Frame(root)
    prog_btns = program_switcher.get_buttons(btn_frame, _update_test_view)
    test_btns = test_switcher.get_buttons(btn_frame, _update_test_view)
    for btn in [prog_btns[0], test_btns[0], test_btns[1], prog_btns[1]]:
        btn.pack(side=tk.LEFT)
    # tk.Button(frame, text="Quit", command=root.quit).pack(side=tk.LEFT)

    _display_test(root, btn_frame, program_ids[0], test_ids[0], all_tests.get(test_ids[0]))

    root.mainloop()
