# main_computer.py
import paho.mqtt.client as mqtt
import json
from Handlers.TangoHandler import TangoHandler
from Handlers.LCardHandler import LCardHandler
from Handlers.IHandler import IHandler
from gui_module import start_gui
from main_computer import MainComputer
import subprocess

class EpicsHandler(IHandler):
    """Обработчик для Epics."""
    pass

def main():
    script_path = r"Tango_SMC/SMCControllerMQTTBridge.py"
    subprocess.Popen(["cmd.exe", "/c", "start", "python", script_path], shell=True)
    #subprocess.Popen(["build-Redis_LCard-Desktop_Qt_5_15_2_MSVC2019_64bit-Debug\Redis_LCard.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    computer = MainComputer(broker_address="localhost", port=1883)
    computer.connect()

    try:
        start_gui(computer)  # Передаем в GUI
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        computer.disconnect()


if __name__ == "__main__":
    main()
