from Utils.MQTTMessage import MQTTMessage
import json
import time

class MQTTCmdMessage(MQTTMessage):
    def __init__(self, topic, device, command, params, time = time.time()):
        super().__init__(topic, device, time)
        self.command = command
        self.params = params or {}

    def to_json(self):
        """Возвращает сообщение в формате JSON."""
        message = {
            "topic": self.topic,
            "command": self.command,
            "params": self.params,
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
            return MQTTCmdMessage(
                topic=data.get("topic"),
                command=data.get("command"),
                params=data.get("params"),
                device=data.get("device"),
                time=data.get("time")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

    def __str__(self):
        """Возвращает строковое представление сообщения."""
        return (f"MQTTMessage(topic={self.topic}, command={self.command}, params={self.params}, "
                f"device={self.device}, time={self.time})")
