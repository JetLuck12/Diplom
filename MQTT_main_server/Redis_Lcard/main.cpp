#include <iostream>
#include "MQTTMessage.h"
#include "mqttcmdmessage.h"
#include "devicemanager.h"
#include "mqtthandler.h"


void on_message(struct mosquitto*, void* obj, const struct mosquitto_message* message) {
    if (message->payloadlen) {
        std::cout << "Message received\n";
        auto* manager = static_cast<DeviceManager*>(obj);

        // Преобразуем payload в строку
        std::string payload(static_cast<char*>(message->payload), message->payloadlen);

        std::cout << payload << "\n";

        try {
            // Десериализуем MQTTMessage
            MQTTCmdMessage mqttMsg = MQTTCmdMessage::fromJson(message->topic, payload);

            // Передаём в обработчик команд
            manager->handle_command(mqttMsg);
        } catch (const std::exception& e) {
            std::cerr << "Ошибка при разборе JSON: " << e.what() << std::endl;
        }
    }
}

int main() {
    try {
        std::string local = "localhost";
        std::string non_local = "192.168.98.20";

        bool is_test = true;
        std::cout << "Connecting to server on " << (is_test ? local : non_local) << "\n";
        MQTTHandler mqtt(local, 1883);
        if (!mqtt.connect()) {
            std::cerr << "Failed to connect to MQTT broker." << std::endl;
            return 1;
        }

        DeviceManager manager(is_test, mqtt);
        manager.init();

        // Подписка на топик с командами
        mqtt.subscribe("lcard/commands", [&manager](const std::string& message) {
            std::cout << "Message received" << message << "\n";
            MQTTCmdMessage msg = MQTTCmdMessage::fromJson("lcard/commands", message);
            manager.handle_command(msg);
        });

        std::cout << "DeviceManager is running. Waiting for commands..." << std::endl;
        while (true) {
            // Бесконечный цикл для работы с устройством
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        mqtt.disconnect();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    } catch (...){
        std::cout << "Error" << std::endl;
    }

    return 0;
}
