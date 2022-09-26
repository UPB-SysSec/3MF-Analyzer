import json
import random
import threading
import traceback

import adsk.cam
import adsk.core
import adsk.fusion

app = None
ui = adsk.core.UserInterface.cast(None)
handlers = []
stopFlag = None
myCustomEvent = "MyCustomEventId"
customEvent = None


# The event handler that responds to the custom event being fired.
class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            # Make sure a command isn't running before changes are made.
            if ui.activeCommand != "SelectCommand":
                ui.commandDefinitions.itemById("SelectCommand").execute()
            app = adsk.core.Application.get()
            while app.documents.count > 1:
                app.documents.item(0).close(False)
        except:
            if ui:
                ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


# The class for the new thread.
class MyThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        app = adsk.core.Application.get()
        while not self.stopped.wait(2):
            if app.documents.count == 2:
                app.fireCustomEvent(myCustomEvent, "")


def run(context):
    global ui
    global app
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        global customEvent
        customEvent = app.registerCustomEvent(myCustomEvent)
        onThreadEvent = ThreadEventHandler()
        customEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        global stopFlag
        stopFlag = threading.Event()
        myThread = MyThread(stopFlag)
        myThread.start()
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))


def stop(context):
    try:
        if handlers.count:
            customEvent.remove(handlers[0])
        stopFlag.set()
        app.unregisterCustomEvent(myCustomEvent)
    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
