# main_computer.py
import paho.mqtt.client as mqtt
import json
from TangoHandler import TangoHandler
from LCardHandler import LCardHandler
from IHandler import IHandler


class RedisHandler(IHandler):
    """Обработчик для Redis."""
    pass


class EpicsHandler(IHandler):
    """Обработчик для Epics."""
    pass


class MainComputer:
    """Главный компьютер."""
    def __init__(self, broker_address: str, port: int, client_id: str = "main_computer"):
        self.broker_address = broker_address
        self.port = port
        self.client_id = client_id

        # Инициализация MQTT клиента
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Инициализация обработчиков участников
        self.handlers = {
            #"smc": TangoHandler("smc", self.client),
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
            print("Connected to MQTT broker!")
            # Подписываемся только на каналы data и errors
            for participant in self.handlers:
                for channel in ["data", "errors"]:
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
            command = input("Write command:")
            command = command.split(" ")
            computer.handlers["lcard"].send_command(command[0], command[1] if len(command) > 1 else "", command[2] if len(command) > 2 else "")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        computer.disconnect()


if __name__ == "__main__":
    main()
