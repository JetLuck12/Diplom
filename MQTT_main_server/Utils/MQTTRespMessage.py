from Utils.MQTTMessage import MQTTMessage
import time
import json

class MQTTRespMessage(MQTTMessage):
    def __init__(self, topic, device, response : json, time = time.time()):
        super().__init__(topic, device, time)
        self.response : json = response

    def to_json(self):
        """Возвращает сообщение в формате JSON."""
        message = {
            "topic": self.topic,
            "device": self.device,
            "response": json.dumps(self.response),
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
                response=json.loads(data.get("response")),
                time=data.get("time")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

    def __str__(self):
        """Возвращает строковое представление сообщения."""
        return (f"MQTTMessage(topic={self.topic}, "
                f"device={self.device}, "
                f"responce={self.response}, time={self.time}")
