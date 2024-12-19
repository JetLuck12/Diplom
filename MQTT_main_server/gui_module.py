import sys
import json
import pyqtgraph as pg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from datetime import datetime


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

    def update_data(self, timestamp, value):
        # Преобразуем timestamp в "час:минута:секунда"
        readable_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
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

        self.argument_input = QLineEdit()
        self.send_button = QPushButton("Отправить команду")
        self.error_status = QTextEdit()
        self.error_status.setReadOnly(True)

        # Компоновка
        command_layout = QHBoxLayout()
        command_layout.addWidget(QLabel("Устройство:"))
        command_layout.addWidget(self.device_selector)
        command_layout.addWidget(QLabel("Команда:"))
        command_layout.addWidget(self.command_selector)
        command_layout.addWidget(QLabel("Аргументы:"))
        command_layout.addWidget(self.argument_input)
        command_layout.addWidget(self.send_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(command_layout)
        main_layout.addWidget(QLabel("Ошибки и статус:"))
        main_layout.addWidget(self.error_status)

        self.setLayout(main_layout)

        # Подключение сигналов
        self.device_selector.currentTextChanged.connect(self.update_command_list)
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

    def send_command(self):
        """Отправляет команду через MQTT."""
        device = self.device_selector.currentText()
        command = self.command_selector.currentText()
        args = self.argument_input.text()

        payload = {
            "command": command,
            "params": {"args": args}
        }
        topic = f"{device}/commands"
        self.mqtt_client.client.publish(topic, json.dumps(payload))
        self.error_status.append(f"Отправлено: {payload}")


class MainWindow(QMainWindow):
    def __init__(self, mqtt_handler=None):
        super().__init__()
        self.mqtt_handler = mqtt_handler

        # Основной интерфейс
        self.setWindowTitle("Управление проектом")
        self.resize(800, 600)

        # Вкладки
        self.tabs = QTabWidget()
        self.data_tab = DataTab(mqtt_handler)
        self.control_tab = ControlTab(mqtt_handler)

        self.tabs.addTab(self.data_tab, "Данные")
        self.tabs.addTab(self.control_tab, "Управление")

        self.setCentralWidget(self.tabs)

        # Таймер для обновления данных
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start(100)

    def fetch_data(self):
        payload = {
            "command": "get_data",
            "params": {"args": ""}
        }
        topic = "lcard/commands"
        self.mqtt_handler.client.publish(topic, json.dumps(payload))
        """Запрашивает данные у обработчика и обновляет интерфейс."""
        if self.mqtt_handler:
            try:
                print("try to fetch data")
                # Запрос последних данных у обработчика
                last_data = self.mqtt_handler.get_handler("lcard").get_data()
                if last_data:
                    timestamp = last_data.get("time")
                    value = last_data.get("value")
                    if timestamp is not None and value is not None:
                        self.data_tab.update_data(timestamp, value)
            except Exception as e:
                print(f"Ошибка при получении данных: {e}")



def start_gui(mqtt_handler):
    app = QApplication(sys.argv)
    main_window = MainWindow(mqtt_handler)
    main_window.show()
    sys.exit(app.exec_())
