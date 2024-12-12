# This Python file uses the following encoding: utf-8
from IHandler import IHandler
import paho.mqtt.client as mqtt
import json


class TangoHandler(IHandler):
    """Обработчик для взаимодействия с SMC через MQTT."""
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        super().__init__(name, mqtt_client)
        self.smc_command_topic = f"{name}/commands"
        self.smc_data_topic = f"{name}/data"
        self.smc_errors_topic = f"{name}/errors"
        self.error_state = "Stable"  # Хранит текущее состояние ошибки
        self.last_data = None  # Хранит последние полученные данные

        # Подписка на каналы
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe(self.smc_data_topic)
        self.mqtt_client.subscribe(self.smc_errors_topic)
        print(f"[TangoHandler] Subscribed to topics: {self.smc_data_topic}, {self.smc_errors_topic}")

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
        self.mqtt_client.publish(self.smc_command_topic, json.dumps(payload))
        print(f"[TangoHandler] Sent command to {self.smc_command_topic}: {payload}")

    def is_error(self):
        """
        Проверяет состояние ошибки.

        :return: Название ошибки (в данном случае "1"), если ошибка есть, иначе 0.
        """
        return self.error_state

    def get_data(self):
        """
        Возвращает последние полученные данные.

        :return: Последние данные или None, если данных нет.
        """
        return self.last_data

    def on_message(self, client, userdata, message):
        """
        Обработка входящих сообщений MQTT.
        """
        topic = message.topic
        payload = message.payload.decode('utf-8')

        try:
            data = json.loads(payload)
            if topic == self.smc_data_topic:
                self.last_data = data
                print(f"[TangoHandler] Data received: {data}")
            elif topic == self.smc_errors_topic:
                self.error_state = data["error"]
                print(f"[TangoHandler] Error received: {data}")
        except json.JSONDecodeError:
            print(f"[TangoHandler] Failed to decode message on topic {topic}: {payload}")
