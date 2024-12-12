# This Python file uses the following encoding: utf-8
from IHandler import IHandler
import paho.mqtt.client as mqtt
import json


class RedisHandler(IHandler):
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        super().__init__(name, mqtt_client)
        self.redis_command_topic = f"{name}/commands"
        self.redis_data_topic = f"{name}/data"
        self.redis_errors_topic = f"{name}/errors"
        self.error_state = "Stable"  # Хранит текущее состояние ошибки
        self.last_data = None  # Хранит последние полученные данные

        # Подписка на каналы
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.subscribe(self.redis_data_topic)
        self.mqtt_client.subscribe(self.redis_errors_topic)
        print(f"[RedisHandler] Subscribed to topics: {self.redis_data_topic}, {self.redis_errors_topic}")
