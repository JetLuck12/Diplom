# This Python file uses the following encoding: utf-8
import paho.mqtt.client as mqtt
import json


class IHandler:
    """Базовый класс для обработчиков участников."""
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        self.name = name
        self.mqtt_client = mqtt_client

    def send_message(self, channel: str, message: dict):
        """Отправка сообщений в канал."""
        topic = f"{self.name}/{channel}"
        payload = json.dumps(message)
        self.mqtt_client.publish(topic, payload)
        print(f"Sent to {topic}: {message}")
