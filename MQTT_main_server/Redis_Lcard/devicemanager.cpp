#include "devicemanager.h"
#include <iostream>
#include <sstream>
#include <ctime>

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
                std::this_thread::sleep_for(std::chrono::seconds(1)); // Частота измерений
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

void DeviceManager::handle_command(const std::string& command_json, MQTTHandler& mqtt) {
    try {
        // Разбираем JSON-команду
        auto command_data = json::parse(command_json);

        std::string command = command_data.at("command");
        if (command == "start") {
            printf("statring");
            start();
            mqtt.publish("lcard/status", R"({"status":"started"})");
        } else if (command == "stop") {
            stop();
            mqtt.publish("lcard/status", R"({"status":"stopped"})");
        } else if (command == "get_data") {
            send_data(mqtt);
        } else if (command == "get_data_since") {
            if (command_data.contains("timestamp")) {
                int timestamp = command_data.at("timestamp");
                send_data_since(timestamp, mqtt);
            } else {
                mqtt.publish("lcard/errors", R"({"error":"Missing timestamp for get_data_since"})");
            }
        } else {
            mqtt.publish("lcard/errors", R"({"error":"Unknown command"})");
        }
    } catch (const json::exception& e) {
        mqtt.publish("lcard/errors", R"({"error":"Invalid JSON format"})");
    }
}

void DeviceManager::collect_data(const std::string& since, MQTTHandler& mqtt) {
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

    mqtt.publish("device/data", message.str());
    std::cout << "Data sent: " << message.str() << std::endl;
}

void DeviceManager::measure_and_store() {
    float value = device->get_data();
    std::time_t timestamp = std::time(nullptr);

    std::lock_guard<std::mutex> lock(data_mutex);
    data[timestamp] = value;
    std::cout << "Data collected: " << timestamp << " -> " << value << std::endl;
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

void DeviceManager::send_data(MQTTHandler& mqtt) {
    json response;

    if (!data.empty()) {
        // Получаем последний элемент в std::map
        auto last_entry = std::prev(data.end());
        response["time"] = last_entry->first;
        response["value"] = last_entry->second;
    } else {
        // Если данных нет, отправляем сообщение об этом
        response["error"] = "No data available";
    }

    mqtt.publish("lcard/data", response.dump());
}

void DeviceManager::send_data_since(int timestamp, MQTTHandler& mqtt) {
    json response;
    response["data"] = json::array();

    for (const auto& [time, value] : data) {
        if (time >= timestamp) {
            response["data"].push_back({{"time", time}, {"value", value}});
        }
    }

    mqtt.publish("lcard/data", response.dump());
}

void DeviceManager::enforce_data_limit() {
    while (data.size() > MAX_DATA_SIZE) {
        // Удаляем элемент с наименьшим ключом (самое старое значение)
        data.erase(data.begin());
    }
}

