# This Python file uses the following encoding: utf-8
from Handlers.IHandler import IHandler
from Utils.MQTTMessage import MQTTMessage
import paho.mqtt.client as mqtt
import json


class TangoHandler(IHandler):
    """Обработчик для взаимодействия с SMC через MQTT."""
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        super().__init__(name, mqtt_client)
        self.smc_command_topic = f"{name}/commands"
        self.smc_inner_data_topic = f"{name}/inner_data"
        self.smc_data_topic = f"{name}/data"
        self.smc_errors_topic = f"{name}/errors"
        self.error_state = "Stable"  # Хранит текущее состояние ошибки
        self.last_data = None  # Хранит последние полученные данные
        self.inner_data_flag = False
        self.inner_data : json

        # Подписка на каналы
        #self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe(self.smc_data_topic)
        self.mqtt_client.message_callback_add(self.smc_data_topic, self.on_smc_data)
        self.mqtt_client.message_callback_add(self.smc_errors_topic, self.on_smc_error)
        self.mqtt_client.message_callback_add(self.smc_inner_data_topic, self.on_smc_inner_data)
        self.mqtt_client.subscribe(self.smc_errors_topic)
        print(f"[TangoHandler] Subscribed to topics: {self.smc_data_topic}, {self.smc_errors_topic}")

        self.axes = []

        self.commands = {
                    "move": {"params": ["axis", "position"], "description": "Move to position"},
                    "stop": {"params": ["axis"], "description": "Stop movement"},
                    "add": {"params": ["axis"], "description": "Add a device"},
                    "delete": {"params": ["axis"], "description": "Delete a device"},
                    "get_state": {"params": ["axis"], "description": "Get the state of the axis"},
                    "get_position": {"params": ["axis"], "description": "Get the position of the axis"},
                }

    def send_command(self, command: str, axis: int, args: dict):
        """
        Отправляет команду в MQTT для SMCControllerMQTTBridge.

        :param command: Название команды
        :param axis: Ось для команды
        :param args: Аргументы команды
        """
        payload = {
            "command": command,
            "axis": axis,
            "params": args
        }
        if command == "add" and not axis in self.axes:
            self.axes.append(axis)
        self.mqtt_client.publish(self.smc_command_topic, json.dumps(payload))
        print(f"[TangoHandler] Sent command to {self.smc_command_topic}: {payload}")

    def is_error(self):
        """
        Проверяет состояние ошибки.

        :return: Название ошибки, если ошибка есть, иначе 0.
        """
        return self.error_state

    def get_data(self):
        """
        Возвращает последние полученные данные.

        :return: Последние данные или None, если данных нет.
        """
        return self.last_data

    def on_smc_data(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = json.loads(payload)
            self.last_data = data
            self.info_tab.error_status.append(f"[TangoHandler] Data received: {data}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")

    def on_smc_inner_data(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = json.loads(payload)
            self.inner_data = data
            self.inner_data_flag = True
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")

    def on_smc_error(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = json.loads(payload)
            self.error_state = data["error"]
            self.info_tab.error_status.append(f"[TangoHandler] Error received: {data}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")


    def get_available_commands(self):
        """Возвращает список доступных команд."""
        return self.commands

    def get_commands_details(self, command):
        return self.commands[command]

    def get_axis_pos(self, axis : int):
        self.inner_data_flag = False
        self.send_command("get_position", axis, [])
        while (not self.inner_data_flag):
            pass
        self.inner_data_flag = False
        return self.inner_data


