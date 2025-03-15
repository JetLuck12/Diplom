from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QHBoxLayout
)
from Utils.MQTTCmdMessage import MQTTCmdMessage

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
        payload = MQTTCmdMessage(topic=topic,
                    command=command,
                    params=params,
                    device=device)

        handler.send_command(payload)
        #self.mqtt_client.client.publish(topic, payload.to_json())
        #self.error_status.append(f"Отправлено: {payload.__str__()}")


