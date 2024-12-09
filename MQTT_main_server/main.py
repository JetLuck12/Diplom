# main_computer.py
import paho.mqtt.client as mqtt
import json

class ParticipantHandler:
    """Базовый класс для обработчиков участников."""
    def __init__(self, name: str, mqtt_client: mqtt.Client):
        self.name = name
        self.mqtt_client = mqtt_client

    def process_message(self, topic: str, data: dict):
        """Обработка сообщений (переопределяется в наследниках)."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def send_message(self, channel: str, message: dict):
        """Отправка сообщений."""
        topic = f"{self.name}/{channel}"
        payload = json.dumps(message)
        self.mqtt_client.publish(topic, payload)
        print(f"Sent to {topic}: {message}")


class RedisHandler(ParticipantHandler):
    def process_message(self, topic: str, data: dict):
        if "commands" in topic:
            self.handle_command(data)
        elif "data" in topic:
            self.handle_data(data)
        elif "errors" in topic:
            self.handle_error(data)

    def handle_command(self, data: dict):
        print(f"[Redis] Command received: {data}")
        # Пример обработки команды
        if data.get("action") == "start":
            response = {"status": "started", "message": "Redis started"}
            self.send_message("data", response)

    def handle_data(self, data: dict):
        print(f"[Redis] Data received: {data}")
        response = {"status": "received", "processed_data": data}
        self.send_message("data", response)

    def handle_error(self, data: dict):
        print(f"[Redis] Error received: {data}")
        response = {"status": "error_acknowledged", "error": data}
        self.send_message("errors", response)


class TangoHandler(ParticipantHandler):
    def process_message(self, topic: str, data: dict):
        if "commands" in topic:
            self.handle_command(data)
        elif "data" in topic:
            self.handle_data(data)
        elif "errors" in topic:
            self.handle_error(data)

    def handle_command(self, data: dict):
        print(f"[Tango] Command received: {data}")
        if data.get("action") == "init":
            response = {"status": "initialized", "message": "Tango initialized"}
            self.send_message("data", response)

    def handle_data(self, data: dict):
        print(f"[Tango] Data received: {data}")
        response = {"status": "processed", "result": data}
        self.send_message("data", response)

    def handle_error(self, data: dict):
        print(f"[Tango] Error received: {data}")
        response = {"status": "error_handled", "error_details": data}
        self.send_message("errors", response)


class EpicsHandler(ParticipantHandler):
    def process_message(self, topic: str, data: dict):
        if "commands" in topic:
            self.handle_command(data)
        elif "data" in topic:
            self.handle_data(data)
        elif "errors" in topic:
            self.handle_error(data)

    def handle_command(self, data: dict):
        print(f"[Epics] Command received: {data}")
        if data.get("action") == "shutdown":
            response = {"status": "shutdown_complete", "message": "Epics shutdown completed"}
            self.send_message("data", response)

    def handle_data(self, data: dict):
        print(f"[Epics] Data received: {data}")
        response = {"status": "acknowledged", "data": data}
        self.send_message("data", response)

    def handle_error(self, data: dict):
        print(f"[Epics] Error received: {data}")
        response = {"status": "error_resolved", "error_info": data}
        self.send_message("errors", response)


class MainComputer:
    def __init__(self, broker_address: str, port: int, client_id: str = "main_computer"):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id

        # Инициализация MQTT клиента
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Инициализация обработчиков участников
        self.handlers = {
            "redis": RedisHandler("redis", self.client),
            "tango": TangoHandler("tango", self.client),
            "epics": EpicsHandler("epics", self.client),
        }

    def connect(self):
        """Подключение к брокеру."""
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()
        print(f"Connecting to broker at {self.broker_address}:{self.port}...")

    def disconnect(self):
        """Отключение от брокеру."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from broker.")

    def on_connect(self, client, userdata, flags, rc):
        """Обработчик подключения."""
        if rc == 0:
            print("Connected to MQTT broker!")
            # Подписываемся на все топики участников
            for participant in self.handlers:
                for channel in ["commands", "data", "errors"]:
                    topic = f"{participant}/{channel}"
                    client.subscribe(topic)
                    print(f"Subscribed to {topic}")
        else:
            print(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, message):
        """Обработчик сообщений."""
        topic = message.topic
        payload = message.payload.decode("utf-8")
        try:
            data = json.loads(payload)  # Парсим JSON из сообщения
            print(f"Received on {topic}: {data}")
            participant = topic.split("/")[0]
            if participant in self.handlers:
                self.handlers[participant].process_message(topic, data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from topic {topic}: {payload}")


def main():
    # Создаем экземпляр MainComputer
    computer = MainComputer(broker_address="localhost", port=1883)

    # Подключаемся к брокеру
    try:
        computer.connect()

        while True:
            # Пример отправки сообщений
            computer.handlers["redis"].send_message("commands", {"action": "start"})
            computer.handlers["tango"].send_message("data", {"value": 42})
            computer.handlers["epics"].send_message("errors", {"error": "Connection lost"})
            input("Press Enter to send next messages or Ctrl+C to exit...")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        computer.disconnect()

if __name__ == "__main__":
    main()
