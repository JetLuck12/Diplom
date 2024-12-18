#pragma once
#include <string>
#include <memory>
#include <map>
#include "DeviceInterface.h"
#include "MockDevice.h"
#include "LcardDevice.h"
#include <mosquitto.h>
#include "mqtthandler.h"
#include "json.hpp"

inline std::unique_ptr<DeviceInterface> create_device(bool test_flag) {
    if (test_flag) {
        // Возвращаем экземпляр имитационного устройства
        return create_mock_device();
    } else {
        // Возвращаем экземпляр реального устройства
        return create_real_device();
    }
}

class DeviceManager {
public:
    explicit DeviceManager(bool test_flag)
        : device(create_device(test_flag)), running(false) {}

    bool init();

    void start();

    void stop();

    void handle_command(const std::string& command, MQTTHandler& mqtt);

    void collect_data(const std::string& since, MQTTHandler& mqtt);

    void measure_and_store(); // Новый метод для фонового сбора данных

private:
    std::unique_ptr<DeviceInterface> device;
    bool running;
    std::map<int, float> data; // Map to store time:value pairs
    std::mutex data_mutex; // Для синхронизации доступа к данным
    void collect_data();
    void send_data(MQTTHandler& mqtt);
    void send_data_since(int timestamp, MQTTHandler& mqtt);
};
