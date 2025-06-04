# This Python file uses the following encoding: utf-8
from Handlers.IHandler import IHandler
from Utils.MQTTMessage import MQTTMessage
from Utils.MQTTCmdMessage import MQTTCmdMessage
from Utils.MQTTRespMessage import MQTTRespMessage
import paho.mqtt.client as mqtt
import json
import time
from Utils.Sync_Data import Sync_Data


class TangoHandler(IHandler):
    """Обработчик для взаимодействия с SMC через MQTT."""
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        super().__init__(name, mqtt_client)
        self.smc_command_topic = "smc/commands"
        self.smc_inner_command_topic = "smc/inner_commands"
        self.smc_inner_data_topic = "smc/inner_data"
        self.smc_data_topic = "smc/data"
        self.smc_errors_topic = "smc/errors"
        self.error_state = "Stable"  # Хранит текущее состояние ошибки
        self.last_data = None  # Хранит последние полученные данные
        self.inner_data  = Sync_Data()

        # Подписка на каналы
        #self.mqtt_client.on_message = self.on_message

        print(f"[TangoHandler] Subscribed to topics: {self.smc_data_topic}, {self.smc_errors_topic}")

        self.axes = []

        self.commands = {
                    "move": {"params": ["axis", "position"], "description": "Move to position"},
                    "stop": {"params": ["axis"], "description": "Stop movement"},
                    "home": {"params": ["axis"], "description": "Move motor in initial position"},
                    "get_state": {"params": ["axis"], "description": "Get the state of the axis"},
                    "get_position": {"params": ["axis"], "description": "Get the position of the axis"},
                }

    def subscribe(self):
        self.mqtt_client.subscribe(self.smc_data_topic)
        self.mqtt_client.subscribe(self.smc_inner_data_topic)
        self.mqtt_client.subscribe(self.smc_errors_topic)

    def set_callback(self):
        self.mqtt_client.message_callback_add(self.smc_data_topic, self.on_smc_data)
        self.mqtt_client.message_callback_add(self.smc_errors_topic, self.on_smc_error)
        self.mqtt_client.message_callback_add(self.smc_inner_data_topic, self.on_smc_inner_data)

    def send_command(self, msg : MQTTMessage):
        """
        Отправляет команду в MQTT для SMCControllerMQTTBridge.

        :param msg: Сообщение, завернутое в MQTTMessage
        """
        self.mqtt_client.publish(msg.topic, msg.to_json())
        print(f"[TangoHandler] Sent command to {msg.topic}: {msg}")

    def send_inner_command(self, msg : MQTTMessage):
        """
        Отправляет команду в MQTT для SMCControllerMQTTBridge.

        :param msg: Сообщение, завернутое в MQTTMessage
        """
        self.send_command(msg)
        print(f"[TangoHandler] Sent command to {msg.topic}: {msg}")
        return self.inner_data.read_value()


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
        print(message)
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = MQTTRespMessage.from_json(payload)
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
            data = MQTTRespMessage.from_json(payload)
            self.inner_data.write_value(data.response)
            print(f"Received inner data: {data.response}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")

    def on_smc_error(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = MQTTRespMessage.from_json(payload)
            self.error_state = data.response["error"]
            context = data.response["context"]
            self.info_tab.error_status.append(f"[TangoHandler] Error received while executing {context}: {self.error_state}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")


    def get_available_commands(self):
        """Возвращает список доступных команд."""
        return self.commands

    def get_commands_details(self, command):
        return self.commands[command]

    def get_motors(self):
        msg = MQTTCmdMessage("smc/inner_commands", "smc", "get_motors", {})
        return self.send_inner_command(msg)



