#include <iostream>
#include "devicemanager.h"
#include "mqtthandler.h"

void on_message(struct mosquitto*, void* obj, const struct mosquitto_message* message) {
    if (message->payloadlen) {
        auto* manager = static_cast<DeviceManager*>(obj);
        std::string command(static_cast<char*>(message->payload), message->payloadlen);
        MQTTHandler mqtt("localhost", 1883);
        manager->handle_command(command, mqtt);
    }
}

int main() {
    try {
        MQTTHandler mqtt("localhost", 1883);
        if (!mqtt.connect()) {
            std::cerr << "Failed to connect to MQTT broker." << std::endl;
            return 1;
        }

        DeviceManager manager(true); // false - реальное устройство
        manager.init();

        // Настраиваем callback для обработки сообщений
        mosquitto_message_callback_set(mqtt.get_mosq(), on_message);
        mosquitto_user_data_set(mqtt.get_mosq(), &manager);
        mqtt.subscribe("lcard/commands");

        std::cout << "Listening for MQTT commands...\n";
        mosquitto_loop_forever(mqtt.get_mosq(), -1, 1);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    return 0;
}
