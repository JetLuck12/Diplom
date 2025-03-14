from Utils.MQTTMessage import MQTTMessage
import time
import json

class MQTTRespMessage(MQTTMessage):
    def __init__(self, topic, device, response, time = time.time()):
        super().__init__(topic, device, time)
        self.response = response

    def to_json(self):
        """Возвращает сообщение в формате JSON."""
        message = {
            "topic": self.topic,
            "device": self.device,
            "response": self.response,
            "time": self.time
        }
        message = json.dumps(message)
        return message

    @staticmethod
    def from_json(json_data):
        """Создает объект MQTTMessage из JSON строки."""
        try:
            data = json.loads(json_data)
            return MQTTRespMessage(
                topic=data.get("topic"),
                device=data.get("device"),
                time=data.get("time")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

    def __str__(self):
        """Возвращает строковое представление сообщения."""
        return (f"MQTTMessage(topic={self.topic},"
                f"device={self.device}, time={self.time}")
