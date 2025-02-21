# This Python file uses the following encoding: utf-8
import paho.mqtt.client as mqtt
import json
from Handlers.IHandler import IHandler
import gui_module


class LCardHandler(IHandler):
    """Обработчик для взаимодействия с LCard через MQTT."""

    def __init__(self, name: str, mqtt_client: mqtt.Client):
        super().__init__(name, mqtt_client)
        self.command_topic = f"{name}/commands"  # Топик для отправки команд
        self.data_topic = f"{name}/data"        # Топик для получения данных
        self.error_topic = f"{name}/errors"     # Топик для получения ошибок
        self.status_topic = f"{name}/status"     # Топик для получения статуса

        self.last_data = None                   # Последние полученные данные
        self.error_state = None                 # Последнее состояние ошибок

        self.data_tab : gui_module.DataTab = None
        self.info_tab : gui_module.ControlTab = None
        # Настраиваем подписки на необходимые топики
        #self.mqtt_client.on_message = self.on_message
        self.mqtt_client.message_callback_add(self.data_topic, self.on_lcard_data)
        self.mqtt_client.message_callback_add(self.error_topic, self.on_lcard_error)
        self.mqtt_client.subscribe(self.data_topic)
        self.mqtt_client.subscribe(self.error_topic)
        print(f"[LCardHandler] Subscribed to topics: {self.data_topic}, {self.error_topic}")

        self.commands = {
                    "start": {"params": [], "description": "Start measurement"},
                    "stop": {"params": [], "description": "Stop measurement"},
                    "get_data": {"params": [], "description": "Get data"},
                    "get_data_since": {"params": ["timestamp"], "description": "Get data since timestamp"},
                }

    def send_command(self, command: str, axis: int = 0, args: dict = None):
        """
        Отправляет команду в MQTT для LCard.

        :param command: Название команды (start, stop, get_data, get_data_since)
        :param axis: Номер оси (для совместимости с IHandler, не используется в LCard)
        :param args: Дополнительные параметры команды (например, timestamp для get_data_since)
        """
        if (command == "get_data_since"):
            self.data_tab.data.clear()
        payload = {"command": command}
        if args:
            payload.update(args)

        self.mqtt_client.publish(self.command_topic, json.dumps(payload))
        print(f"[LCardHandler] Sent command to {self.command_topic}: {payload}")
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
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = json.loads(payload)
            if data.get("type") == "single":
                values = data.get("data")
                timestamp = values[0].get("time")
                value = values[0].get("value")
                if timestamp is not None and value is not None:
                    self.data_tab.update_data(timestamp, value)
                print(f"[LCardHandler] Single data received: {data}")
            else:
                values = data.get("data")
                print(values)
                for item in values:
                    time = item.get("time")
                    value = item.get("value")
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
            data = json.loads(payload)
            self.info_tab.error_status.append(f"[LCardHandler] Error received: {data}")
        except json.JSONDecodeError:
            self.info_tab.error_status.append(f"[LCardHandler] Failed to decode message on topic {topic}: {payload}")

    def get_available_commands(self):
        """Возвращает список доступных команд."""
        return self.commands

    def get_commands_details(self, command):
        return self.commands[command]
