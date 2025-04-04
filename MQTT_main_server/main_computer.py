import paho.mqtt.client as mqtt
import json
from Handlers.TangoHandler import TangoHandler
from Handlers.LCardHandler import LCardHandler

class MainComputer:
    """Главный компьютер."""
    def __init__(self, broker_address: str, port: int, client_id: str):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id

        # Инициализация MQTT клиента
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Инициализация обработчиков участников
        self.handlers = {
            "smc": TangoHandler("smc", self.client),
            "lcard": LCardHandler("lcard", self.client)
        }

    def connect(self):
        """Подключение к брокеру."""
        self.client.connect(self.broker_address, self.port)
        self.client.loop_start()
        print(f"Connecting to broker at {self.broker_address}:{self.port}...")

    def disconnect(self):
        """Отключение от брокера."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from broker.")

    def on_connect(self, client, userdata, flags, rc):
        """Обработчик подключения."""
        if rc == 0:
            for handler in self.handlers.values():
                handler.subscribe()
                handler.set_callback()
            print("Connected to MQTT broker!")
        else:
            print(f"Connection failed with code {rc}")

    def get_handler(self, device_name):
            return self.handlers.get(device_name)

    def on_message(self, client, userdata, message):
        """Обработчик сообщений."""
        print(message)
        topic = message.topic
        payload = message.payload.decode("utf-8")
        try:
            data = json.loads(payload)  # Парсим JSON из сообщения
            print(f"Received on {topic}: {data}")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from topic {topic}: {payload}")
