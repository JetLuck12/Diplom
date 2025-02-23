#include <iostream>
#include "devicemanager.h"
#include "mqtthandler.h"

void on_message(struct mosquitto*, void* obj, const struct mosquitto_message* message) {
    if (message->payloadlen) {
        auto* manager = static_cast<DeviceManager*>(obj);
        std::string command(static_cast<char*>(message->payload), message->payloadlen);
        MQTTHandler mqtt("localhost", 1883);
        manager->handle_command(command);
    }
}

int main() {
    try {
        MQTTHandler mqtt("localhost", 1883);
        if (!mqtt.connect()) {
            std::cerr << "Failed to connect to MQTT broker." << std::endl;
            return 1;
        }

        DeviceManager manager(true, mqtt);
        manager.init();

        // Подписка на топик с командами
        mqtt.subscribe("lcard/commands", [&manager, &mqtt](const std::string& message) {
            manager.handle_command(message);
        });

        std::cout << "DeviceManager is running. Waiting for commands..." << std::endl;
        while (true) {
            // Бесконечный цикл для работы с устройством
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        mqtt.disconnect();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    return 0;
}
