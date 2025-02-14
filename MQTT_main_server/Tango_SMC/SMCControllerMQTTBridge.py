from SMCBaseMotorController import SMCBaseMotorController
from MockSMCMotorHW import MockSMCMotorHW
import paho.mqtt.client as mqtt
import json
import time
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from Utils.MQTTMessage import MQTTMessage

class SMCControllerMQTTBridge:
    def __init__(self, mqtt_broker, mqtt_port, mqtt_topic_prefix, smc_controller):
        """
        Инициализация моста для взаимодействия между SMCBaseMotorController и MQTT.

        :param mqtt_broker: Адрес MQTT брокера
        :param mqtt_port: Порт MQTT брокера
        :param mqtt_topic_prefix: Префикс для топиков MQTT
        :param smc_controller: Объект SMCBaseMotorController
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic_prefix = mqtt_topic_prefix
        self.smc_controller = smc_controller

        # Инициализация MQTT клиента
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        """Подключение к MQTT брокеру."""
        self.client.connect(self.mqtt_broker, self.mqtt_port)
        self.client.loop_start()
        print(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")

    def disconnect(self):
        """Отключение от MQTT брокера."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT broker.")

    def on_connect(self, client, userdata, flags, rc, *args):
        """Обработчик события подключения к брокеру."""
        if rc == 0:
            print("Connected to MQTT broker successfully.")
            # Подписываемся на команды
            command_topic = f"{self.mqtt_topic_prefix}/commands"
            client.subscribe(command_topic)
            print(f"Subscribed to topic: {command_topic}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, *args):
        """Обработчик входящих сообщений."""
        client, userdata, message = args
        topic = message.topic
        print(topic)
        try:
            # Декодируем payload в строку
            message_str = message.payload.decode("utf-8")
            # Выводим JSON-данные
            print("Получено сообщение:", message_str)

        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
        message = MQTTMessage.from_json(message_str)


        if topic != "smc/commands":
            raise Exception(f"bad topic: {topic}")
        try:
            print(f"Received message on topic {topic}: {message.__str__()}")
            self.handle_command(message)
        except json.JSONDecodeError:
            self.publish_error("Invalid JSON format", topic)

    def handle_command(self, message):
        """Обработка команд от MQTT."""
        command = str(message.command)
        axis = str(message.params[0])
        params = str(message.params[1:])

        try:
            if command == "move":
                position = float(params)
                if axis is not None and position is not None:
                    self.smc_controller.StartOne(axis, position)
                    self.publish_data(axis, {"status": "Moving", "position": position})
                else:
                    raise ValueError("Missing axis or position parameter")
            elif command == "stop":
                if axis is not None:
                    self.smc_controller.StopOne(axis)
                    self.publish_data(axis, {"status": "Stopped"})
                else:
                    raise ValueError("Missing axis parameter")
            elif command == "add":
                if axis is not None:
                    self.smc_controller.AddDevice(axis)
                    print("added")
                else:
                    raise ValueError("Missing axis parameter")
            elif command == "delete":
                if axis is not None:
                    self.smc_controller.DeleteDevice(axis)
                else:
                    raise ValueError("Missing axis parameter")
            elif command == "get_state":
                if axis is not None:
                    _, status = self.smc_controller.StateOne(axis)
                    self.publish_data(axis, {"status": status})
                else:
                    raise ValueError("Missing axis parameter")
            elif command == "get_position":
                if axis is not None:
                    position = self.smc_controller.ReadOne(axis)
                    self.publish_data(axis, {"position": position})
                else:
                    raise ValueError("Missing axis parameter")
            else:
                raise ValueError(f"Unknown command: {command}")
        except Exception as e:
            self.publish_error(str(e), f"Command: {command}")

    def publish_data(self, axis, data):
        """Публикация данных в канал `smc/data`."""
        topic = f"{self.mqtt_topic_prefix}/data"
        message = {"axis": axis, "data": data}
        self.client.publish(topic, json.dumps(message))
        print(f"Published data to {topic}: {message}")

    def publish_error(self, error_message, context=""):
        """Публикация ошибок в канал `smc/errors`."""
        topic = f"{self.mqtt_topic_prefix}/errors"
        message = {"error": error_message, "context": context}
        self.client.publish(topic, json.dumps(message))
        print(f"Published error to {topic}: {message}")


def main():

    # Выбор контроллера (Mock или реальный)
    print("Starting SMC Controller MQTT Bridge...")
    test_mode = True  # True для использования MockSMCMotorHW
    smc_controller = MockSMCMotorHW() if test_mode else SMCBaseMotorController(inst=None, props={"Port": "/dev/ttyUSB0"})

    # Создаем MQTT мост
    mqtt_bridge = SMCControllerMQTTBridge(
        mqtt_broker="localhost",
        mqtt_port=1883,
        mqtt_topic_prefix="smc",
        smc_controller=smc_controller
    )

    # Запуск
    try:
        mqtt_bridge.connect()
        print("MQTT Bridge is running. Press Ctrl+C to exit.")
        while True:
            time.sleep(1)  # Основной цикл
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        mqtt_bridge.disconnect()



if __name__ == "__main__":
    main()
