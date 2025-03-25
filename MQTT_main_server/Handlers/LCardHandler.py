# This Python file uses the following encoding: utf-8
import paho.mqtt.client as mqtt
import json
from Handlers.IHandler import IHandler
from GUI.ControlTab import ControlTab
from GUI.DataTab import DataTab
from Utils.MQTTMessage import MQTTMessage
from Utils.MQTTRespMessage import MQTTRespMessage
from PyQt5.QtCore import QTimer


class LCardHandler(IHandler):
    """Обработчик для взаимодействия с LCard через MQTT."""

    def __init__(self, name: str, mqtt_client: mqtt.Client, timer : QTimer = None):
        super().__init__(name, mqtt_client)
        self.command_topic = f"{name}/commands"  # Топик для отправки команд
        self.data_topic = f"{name}/data"        # Топик для получения данных
        self.error_topic = f"{name}/errors"     # Топик для получения ошибок
        self.status_topic = f"{name}/status"     # Топик для получения статуса

        self.last_data = None                   # Последние полученные данные
        self.error_state = None                 # Последнее состояние ошибок

        self.data_tab : DataTab = None
        self.info_tab : ControlTab = None

        self.timer = timer

        # Настраиваем подписки на необходимые топики
        #self.mqtt_client.on_message = self.on_message

        self.commands = {
                    "start": {"params": [], "description": "Start measurement"},
                    "stop": {"params": [], "description": "Stop measurement"},
                    "get_current_data": {"params": [], "description": "Get current data"},
                    "get_data_since": {"params": ["start_timestamp", "end_timestamp"], "description": "Get data since timestamp"},
                    "get_continuous_data" : {"params": [], "description":"get data in real time"}
                }

    def subscribe(self):
        self.mqtt_client.subscribe(self.data_topic)
        self.mqtt_client.subscribe(self.error_topic)

    def set_callback(self):
        self.mqtt_client.message_callback_add(self.data_topic, self.on_lcard_data)
        self.mqtt_client.message_callback_add(self.error_topic, self.on_lcard_error)


    def send_command(self, msg : MQTTMessage):
        """
        Отправляет команду в MQTT для LCard.

        :param command: Название команды (start, stop, get_data, get_data_since)
        :param axis: Номер оси (для совместимости с IHandler, не используется в LCard)
        :param args: Дополнительные параметры команды (например, timestamp для get_data_since)
        """
        if (msg.command == "get_data_since"):
            self.data_tab.data.clear()
        elif msg.command == "start":
            self.timer.start(100)
        elif msg.command == "stop":
            self.timer.stop()

        self.mqtt_client.publish(msg.topic, msg.to_json())
        self.info_tab.error_status.append(f"[LCardHandler] Sent command to {msg.command}: {msg}")
        print(f"[LCardHandler] Sent command to {self.command_topic}: {msg}")
    def get_data(self):
        """
        Возвращает последние полученные данные.

        :return: Последние данные или None, если данных нет.
        """
        return self.last_data

    def is_error(self):
        """
        Проверяет состояние ошибки.

        :return: Последнее состояние ошибок.
        """
        return self.error_state

    def on_lcard_data(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        print(message)
        topic = message.topic
        payload = message.payload.decode('utf-8')
        try:
            msg = MQTTRespMessage.from_json(payload)
            data = msg.response
            if data.get("type") == "single":
                values = data.get("data")
                timestamp, value = list(values.items())[0]
                if timestamp is not None and value is not None:
                    self.data_tab.update_data(int(timestamp), value)
                print(f"[LCardHandler] Single data received: {data}")
            else:
                self.data_tab.data.clear()
                values : dict = data.get("data")
                for time, value in list(values.items()):
                    if time is not None and value is not None:
                        self.data_tab.update_data(time, value)
        except json.JSONDecodeError:
            print(f"[LCardHandler] Failed to decode message on topic {topic}: {payload}")

    def on_lcard_error(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = MQTTRespMessage.from_json(payload)
            self.info_tab.error_status.append(f"[LCardHandler] Error received: {data}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[LCardHandler] Failed to decode message on topic {topic}: {payload}")

    def get_available_commands(self):
        """Возвращает список доступных команд."""
        return self.commands

    def get_commands_details(self, command):
        return self.commands[command]

    def fetch_data(self):
        """Запрашивает данные у обработчика и обновляет интерфейс."""
        try:
            # Запрос последних данных у обработчика
            if self.last_data:
                timestamp = self.last_data.get("time")
                value = self.last_data.get("value")
                if timestamp is not None and value is not None:
                    self.data_tab.update_data(timestamp, value)
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
