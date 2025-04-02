# main.py
from Handlers.IHandler import IHandler
from GUI.gui_module import start_gui
from main_computer import MainComputer
import subprocess

class EpicsHandler(IHandler):
    """Обработчик для Epics."""
    pass

def main():
    script_path = r"Tango_SMC/SMCControllerMQTTBridge.py"
    #subprocess.Popen(["python", script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    #subprocess.Popen(["build-Redis_LCard-Desktop_Qt_5_15_2_MSVC2019_64bit-Debug/Redis_LCard.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    test_flag = True
    address = "localhost" if test_flag else "192.168.98.20"
    handler = MainComputer(broker_address=address, port=1883, client_id="main_computer")
    try:
        start_gui(handler)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
