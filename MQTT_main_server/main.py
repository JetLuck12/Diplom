# main.py
from Handlers.IHandler import IHandler
from gui_module import start_gui
import subprocess

class EpicsHandler(IHandler):
    """Обработчик для Epics."""
    pass

def main():
    script_path = r"Tango_SMC/SMCControllerMQTTBridge.py"
    subprocess.Popen(["cmd.exe", "/c", "start", "python", script_path], shell=True)
    subprocess.Popen(["build-Redis_LCard-Desktop_Qt_5_15_2_MSVC2019_64bit-Debug/Redis_LCard.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    try:
        start_gui()
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
