import json
import time


class MQTTMessage:
    def __init__(self, topic, device=None, time = time.time()):
        """
        Инициализация сообщения MQTT.

        :param topic: MQTT топик для публикации
        :param device: Имя устройства (если необходимо)
        :param time: Время отправки
        """
        self.topic = topic
        self.device = device
        self.time = time

    def to_json(self):
        """Возвращает сообщение в формате JSON."""
        message = {
            "topic": self.topic,
            "device": self.device,
            "time": self.time
        }
        message = json.dumps(message)
        return message

    @staticmethod
    def from_json(json_data):
        """Создает объект MQTTMessage из JSON строки."""
        try:
            data = json.loads(json_data)
            return MQTTMessage(
                topic=data.get("topic"),
                device=data.get("device"),
                time=data.get("time")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

    def __str__(self):
        """Возвращает строковое представление сообщения."""
        return (f"MQTTMessage(topic={self.topic}, device={self.device}")
