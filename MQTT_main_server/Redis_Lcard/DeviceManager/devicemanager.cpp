#include "devicemanager.h"
#include "MQTTMessage.h"
#include "mqttcmdmessage.h"
#include "mqttrespmessage.h"
#include "statusresponse.h"
#include "dataresponse.h"
#include <iostream>
#include <sstream>
#include <ctime>
#include <map>
#include "json.hpp"

using json = nlohmann::json;

bool DeviceManager::init() {
    if (!device->init()) {
        return false;
    }
    return true;
}

void DeviceManager::start() {
    if (!running) {
        device->start();
        running = true;

        // Запускаем поток для сбора данных
        std::thread([this]() {
            while (running) {
                measure_and_store();
                std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Частота измерений
            }
        }).detach();

        std::cout << "Device started.\n";
    }
}

void DeviceManager::stop() {
    if (device) {
        device->stop();
        running = false;
    }
}

void DeviceManager::handle_command(const MQTTCmdMessage& MqttMsg) {
    try {
        // Разбираем JSON-команду
        std::cout << "Message received\n";
        auto command = MqttMsg.getCommand();
        if (command == "start") {
            printf("statring");
            start();
            StatusResponse resp(R"({"status":"started"})");
            MQTTRespMessage msg("lcard/status", resp, "lcard");
            mqtt.publish("lcard/status", msg);
        } else if (command == "stop") {
            stop();
            continuous = false;
            StatusResponse resp(R"({"status":"stopped"})");
            MQTTRespMessage msg("lcard/status", resp, "lcard");
            mqtt.publish("lcard/status", msg);
        } else if (command == "get_current_data") {
            continuous = false;
            send_data();
        } else if (command == "get_continuous_data") {
            continuous = true;
        } else if (command == "get_data_since") {
            continuous = false;
            auto params = MqttMsg.getParams();
            if (!params.empty()) {
                std::string start_str = params.at("start");
                std::string end_str = params.at("params");
                int start_timestamp = start_str == "" ? 0 : std::stoi(start_str);
                int end_timestamp = end_str == "" ? 0 : std::stoi(end_str);
                send_data_since(start_timestamp,end_timestamp);
            } else {
                StatusResponse resp(R"({"error":"Missing timestamp for get_data_since"})");
                MQTTRespMessage msg("lcard/errors", resp, "lcard");
                mqtt.publish("lcard/errors", msg);
            }
        } else {
            StatusResponse resp(R"({"error":"Unknown command"})");
            MQTTRespMessage msg("lcard/errors", resp, "lcard");
            mqtt.publish("lcard/errors", msg);
        }
    } catch (const json::exception& e) {
        StatusResponse resp(R"({"error":"Invalid JSON format"})");
        MQTTRespMessage msg("lcard/errors", resp, "lcard");
        mqtt.publish("lcard/errors", msg);
    }
}

void DeviceManager::collect_data(const std::string& since) {
    std::ostringstream message;
    std::time_t since_timestamp = 0;

    // Конвертируем строку в time_t, если указано время
    if (!since.empty()) {
        try {
            since_timestamp = std::stoll(since);
        } catch (const std::exception&) {
            std::cerr << "Invalid timestamp format: " << since << "\n";
            return;
        }
    }

    std::lock_guard<std::mutex> lock(data_mutex);

    // Генерируем JSON с данными
    message << "{ \"data\": [";
    bool first = true;
    for (const auto& [timestamp, value] : data) {
        if (timestamp >= since_timestamp) {
            if (!first) {
                message << ", ";
            }
            message << "{ \"time\": " << timestamp << ", \"value\": " << value << " }";
            first = false;
        }
    }
    message << "] }";

    //mqtt.publish("device/data", message.str());
    std::cout << "Data sent: " << message.str() << std::endl;
}

using namespace std::chrono;

void DeviceManager::measure_and_store() {
    float value = device->get_data();
    unsigned long long timestamp = duration_cast<milliseconds>(
                                       system_clock::now().time_since_epoch()
                                       ).count();

    std::lock_guard<std::mutex> lock(data_mutex);
    data[timestamp] = value;
    std::cout << "Data collected: " << timestamp << " -> " << value << std::endl;
    if (continuous){
        send_data();
    }
}

void DeviceManager::collect_data() {
    if (running) {
        int current_time = static_cast<int>(std::time(nullptr)); // Текущее время в секундах
        float value = device->get_data();

        // Добавляем новую запись
        data[current_time] = value;

        // Ограничиваем размер данных
        enforce_data_limit();
    }
}

void DeviceManager::send_data() {
    if (!data.empty()) {
        // Получаем последний элемент в std::map
        auto last_entry = std::prev(data.end());
        std::string str_time = std::to_string(last_entry->first);
        double val = last_entry->second;
        DataResponse response("single", std::map<std::string, double>{{str_time, val}});
        MQTTRespMessage msg("lcard/data", response, "lcard");
        mqtt.publish("lcard/data", msg);
    } else {
        // Если данных нет, отправляем сообщение об этом
        StatusResponse resp("No data available");
        MQTTRespMessage msg("lcard/error", resp, "lcard");
        mqtt.publish("lcard/error", msg);
    }
}

void DeviceManager::send_data_since(int start_timestamp,int end_timestamp) {
    std::map<std::string, double> resp_data;
    json response;
    response["type"] = "list";
    response["data"] = json::array();
    for (const auto& [time, value] : data) {
        if (time >= start_timestamp && (end_timestamp == 0 || time <= end_timestamp)) {
            resp_data[std::string{static_cast<char>(time)}] = value;
        }
    }
    DataResponse resp("list", resp_data);
    MQTTRespMessage msg("lcard/data", resp, "lcard");
    mqtt.publish("lcard/data", msg);
}

void DeviceManager::enforce_data_limit() {
    while (data.size() > MAX_DATA_SIZE) {
        // Удаляем элемент с наименьшим ключом (самое старое значение)
        data.erase(data.begin());
    }
}

