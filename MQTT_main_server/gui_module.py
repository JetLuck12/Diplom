import sys
import json
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QHBoxLayout, QFormLayout,
    QFileDialog
)
from datetime import datetime
from Utils.MQTTMessage import MQTTMessage
from main_computer import MainComputer
from Calibrator.Calibrator import Calibrator
from PyQt5.QtCore import QTimer


class DataTab(QWidget):
    def __init__(self, mqtt_handler=None):
        super().__init__()
        self.mqtt_handler = mqtt_handler

        # Последнее значение
        self.last_value_label = QLabel("Последнее значение: N/A")
        self.graph_widget = pg.PlotWidget()
        self.data = []  # Хранит данные [(time, value)]

        layout = QVBoxLayout()
        layout.addWidget(self.last_value_label)
        layout.addWidget(self.graph_widget)

        self.setLayout(layout)

        self.timer = QTimer()

    def update_data(self, timestamp, value):
        # Преобразуем timestamp в "час:минута:секунда"
        #readable_time = datetime.fromtimestamp(timestamp).strftime("%M:%S.%f")
        readable_time = timestamp % 10000
        if len(self.data) != 0 and self.data[-1][0] == readable_time:
            print(f"cal: {self.data[-1]}")
            return
        if len(self.data) > 100:
            self.data.pop(0)
        self.data.append((readable_time, value))
        self.last_value_label.setText(f"Последнее значение: {value} (время: {readable_time})")

        # Обновление графика
        x = [d[0] for d in self.data]
        y = [d[1] for d in self.data]

        self.graph_widget.clear()
        self.graph_widget.plot(range(len(x)), y, pen="b")  # Используем индекс вместо времени для оси X

        # Уменьшение количества меток в зависимости от объема данных
        max_labels = 10  # Максимальное количество меток на оси
        step = max(1, len(x) // max_labels)
        displayed_ticks = [(i, x[i]) for i in range(0, len(x), step)]

        axis = self.graph_widget.getAxis("bottom")
        axis.setTicks([displayed_ticks])

class ControlTab(QWidget):
    def __init__(self, mqtt_client):
        super().__init__()
        self.mqtt_client = mqtt_client

        # Элементы управления
        self.device_selector = QComboBox()
        self.device_selector.addItems(["smc", "lcard"])

        self.command_selector = QComboBox()
        self.command_selector.addItems(["start", "stop", "get_data", "get_data_since"])

        self.arguments_layout = QVBoxLayout()
        self.argument_fields = []

        self.send_button = QPushButton("Отправить команду")
        self.error_status = QTextEdit()
        self.error_status.setReadOnly(True)

        # Компоновка
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Устройство:"))
        command_layout.addWidget(self.device_selector)
        command_layout.addWidget(QLabel("Команда:"))
        command_layout.addWidget(self.command_selector)

        arguments_container = QWidget()
        arguments_container.setLayout(self.arguments_layout)

        main_layout = QVBoxLayout()
        main_layout.addLayout(command_layout)
        main_layout.addWidget(QLabel("Аргументы:"))
        main_layout.addWidget(arguments_container)
        main_layout.addWidget(self.send_button)
        main_layout.addWidget(QLabel("Ошибки и статус:"))
        main_layout.addWidget(self.error_status)

        self.setLayout(main_layout)

        # Подключение сигналов
        self.device_selector.currentTextChanged.connect(self.update_command_list)
        self.command_selector.currentTextChanged.connect(self.update_argument_fields)
        self.send_button.clicked.connect(self.send_command)

        self.update_command_list()

    def update_command_list(self):
        """Обновляет список доступных команд на основе выбранного устройства."""
        selected_device = self.device_selector.currentText()
        handler = self.mqtt_client.get_handler(selected_device)
        self.command_selector.clear()

        if handler:
            commands = handler.get_available_commands()  # Метод для получения команд
            for command, details in commands.items():
                description = details.get("description", "")
                self.command_selector.addItem(f"{command} ({description})", command)

        self.update_argument_fields()

    def update_argument_fields(self):
            """Обновляет поля ввода аргументов на основе выбранной команды."""
            # Очистка текущих полей и меток
            while self.arguments_layout.count():
                item = self.arguments_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.argument_fields = []

            # Получение описания команды
            selected_device = self.device_selector.currentText()
            selected_command = self.command_selector.currentText().split(" ")[0]
            handler = self.mqtt_client.get_handler(selected_device)

            if handler:
                command_details = handler.get_command_details(selected_command)
                if command_details:
                    for arg in command_details.get("params", []):
                        label = QLabel(arg)
                        input_field = QLineEdit()
                        self.arguments_layout.addWidget(label)
                        self.arguments_layout.addWidget(input_field)
                        self.argument_fields.append(input_field)


    def send_command(self):
        """Отправляет команду через MQTT."""
        device = self.device_selector.currentText()
        handler = self.mqtt_client.get_handler(device)
        command = self.command_selector.currentText().split(" ")[0]
        params = [field.text() for field in self.argument_fields]
        topic = f"{device}/commands"
        payload = MQTTMessage(topic=topic,
                    command=command,
                    params=params,
                    device=device)

        handler.send_command(payload)
        #self.mqtt_client.client.publish(topic, payload.to_json())
        #self.error_status.append(f"Отправлено: {payload.__str__()}")



class CalibrationTab(QWidget):
    def __init__(self, calibrator):
        super().__init__()
        self.calibrator = calibrator

        # UI элементы
        self.calibrate_button = QPushButton("Калибровать")
        self.save_config_button = QPushButton("Сохранить конфигурацию")
        self.load_config_button = QPushButton("Загрузить конфигурацию")
        self.calibrate_from_config_button = QPushButton("Калибровать из конфигурации")
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)

        # Компоновка
        layout = QVBoxLayout()
        layout.addWidget(self.calibrate_button)
        layout.addWidget(self.save_config_button)
        layout.addWidget(self.load_config_button)
        layout.addWidget(self.calibrate_from_config_button)
        layout.addWidget(QLabel("Статус:"))
        layout.addWidget(self.status_output)
        self.setLayout(layout)

        # Подключение сигналов
        self.calibrate_button.clicked.connect(self.start_calibration)
        self.save_config_button.clicked.connect(self.save_configuration)
        self.load_config_button.clicked.connect(self.load_configuration)
        self.calibrate_from_config_button.clicked.connect(self.calibrate_from_config)

    def start_calibration(self):
        self.status_output.append("Запуск калибровки...")
        self.calibrator.calibrate()
        self.status_output.append("Калибровка завершена.")

    def save_configuration(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить конфигурацию", "", "JSON Files (*.json)")
        if file_path:
            self.calibrator.save_configuration(file_path)
            self.status_output.append(f"Конфигурация сохранена: {file_path}")

    def load_configuration(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить конфигурацию", "", "JSON Files (*.json)")
        if file_path:
            self.calibrator.load_configuration(file_path)
            self.status_output.append(f"Конфигурация загружена: {file_path}")

    def calibrate_from_config(self):
        self.status_output.append("Запуск калибровки по сохраненной конфигурации...")
        self.calibrator.calibrate_from_config()
        self.status_output.append("Калибровка по конфигурации завершена.")

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

        if "lcard" in self.mqtt_handler.handlers.keys():
            self.data_tab.timer.timeout.connect(self.mqtt_handler.handlers["lcard"].fetch_data)

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

