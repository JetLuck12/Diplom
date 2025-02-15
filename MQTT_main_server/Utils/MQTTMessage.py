import json
import time


class MQTTMessage:
    def __init__(self, topic, command, params=None, device=None,
                 server_timestamp=None, client_response=None, server_received_timestamp=None):
        """
        Инициализация сообщения MQTT.

        :param topic: MQTT топик для публикации
        :param command: Команда для отправки
        :param params: Параметры команды (словарь или None)
        :param device: Имя устройства (если необходимо)
        :param server_timestamp: Время отправки сообщения сервером
        :param client_response: Ответ клиента (данные или статус)
        :param server_received_timestamp: Время получения ответа сервером
        """
        self.topic = topic
        self.command = command
        self.params = params or {}
        self.device = device
        self.server_timestamp = server_timestamp or time.time()
        self.client_response = client_response
        self.server_received_timestamp = server_received_timestamp

    def to_json(self):
        """Возвращает сообщение в формате JSON."""
        message = {
            "command": self.command,
            "params": self.params,
            "device": self.device,
            "server_timestamp": self.server_timestamp,
            "client_response": self.client_response,
            "server_received_timestamp": self.server_received_timestamp,
        }
        message = json.dumps(message)
        return message

    def publish(self, mqtt_client):
        """Публикует сообщение через указанный MQTT клиент."""
        message = self.to_json()
        mqtt_client.publish(self.topic, message)

    @staticmethod
    def from_json(json_data):
        """Создает объект MQTTMessage из JSON строки."""
        try:
            data = json.loads(json_data)
            return MQTTMessage(
                topic=data.get("topic"),
                command=data.get("command"),
                params=data.get("params"),
                device=data.get("device"),
                server_timestamp=data.get("server_timestamp"),
                client_response=data.get("client_response"),
                server_received_timestamp=data.get("server_received_timestamp")
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка декодирования JSON: {e}")

    def set_client_response(self, response, server_received_timestamp=None):
        """Устанавливает ответ клиента и время получения сервером."""
        self.client_response = response
        self.server_received_timestamp = server_received_timestamp or time.time()

    def __str__(self):
        """Возвращает строковое представление сообщения."""
        return (f"MQTTMessage(topic={self.topic}, command={self.command}, params={self.params}, "
                f"device={self.device}, server_timestamp={self.server_timestamp}, "
                f"client_response={self.client_response}, "
                f"server_received_timestamp={self.server_received_timestamp})")
