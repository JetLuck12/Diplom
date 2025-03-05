#pragma once
#include <string>
#include <memory>
#include <map>
#include "DeviceInterface.h"
#include "MQTTMessage.h"
#include "mqttcmdmessage.h"
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
    explicit DeviceManager(bool test_flag, MQTTHandler& mqtt_)
        : device(create_device(test_flag)), running(false), mqtt(mqtt_) {}

    bool init();

    void start();

    void stop();

    void handle_command(const MQTTCmdMessage& command);

    void collect_data(const std::string& since);

    void measure_and_store();

private:
    static constexpr size_t MAX_DATA_SIZE = 100;
    std::unique_ptr<DeviceInterface> device;
    bool running;
    std::map<unsigned long long, float> data;
    std::mutex data_mutex;
    void collect_data();
    void send_data();
    void send_data_since(int start_timestamp, int end_timestamp);
    void enforce_data_limit();
    bool continuous;
    MQTTHandler& mqtt;
};
