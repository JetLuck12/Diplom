import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget
)
from main_computer import MainComputer
from Calibrator.Calibrator import Calibrator
from PyQt5.QtCore import QTimer
from GUI.CalibrationTab import CalibrationTab
from GUI.ControlTab import ControlTab
from GUI.DataTab import DataTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mqtt_handler = MainComputer(broker_address="localhost", port=1883, client_id="main_computer")
        self.mqtt_handler.connect()

        # Основной интерфейс
        self.setWindowTitle("Управление проектом")
        self.resize(800, 600)

        # Вкладки
        self.tabs = QTabWidget()
        self.data_tab = DataTab(self.mqtt_handler)
        self.control_tab = ControlTab(self.mqtt_handler)

        self.timer = QTimer()

        if "lcard" in self.mqtt_handler.handlers.keys():
            self.mqtt_handler.handlers["lcard"].timer = self.timer
            self.timer.timeout.connect(self.mqtt_handler.handlers["lcard"].fetch_data)
            self.timer.start(100)

        for (name, handler) in self.mqtt_handler.handlers.items():
            if (name == "lcard"):
                handler.data_tab = self.data_tab
            handler.info_tab = self.control_tab

        self.calibrator = Calibrator(self.mqtt_handler, -1)
        self.calibrator_tab = CalibrationTab(self.calibrator)

        self.tabs.addTab(self.data_tab, "Данные")
        self.tabs.addTab(self.control_tab, "Управление")
        self.tabs.addTab(self.calibrator_tab, "Конфигурация")

        self.setCentralWidget(self.tabs)

    def closeEvent(self, event):
        self.mqtt_handler.disconnect()
        event.accept()


def start_gui():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

