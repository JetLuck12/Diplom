#include "mqtthandler.h"
#include <iostream>

MQTTHandler::MQTTHandler(const std::string& broker_address, int port)
    : broker_address(broker_address), port(port), mosq(nullptr) {
    mosquitto_lib_init();
    mosq = mosquitto_new(nullptr, true, nullptr);
    if (!mosq) {
        throw std::runtime_error("Failed to initialize Mosquitto instance");
    }
}

MQTTHandler::~MQTTHandler() {
    if (mosq) {
        mosquitto_destroy(mosq);
    }
    mosquitto_lib_cleanup();
}

bool MQTTHandler::connect() {
    int ret = mosquitto_connect(mosq, broker_address.c_str(), port, 60);
    if (ret != MOSQ_ERR_SUCCESS) {
        std::cerr << "Failed to connect to MQTT broker: " << mosquitto_strerror(ret) << std::endl;
        return false;
    }
    return true;
}

void MQTTHandler::disconnect() {
    mosquitto_disconnect(mosq);
}

bool MQTTHandler::publish(const std::string& topic, const std::string& message) {
    int ret = mosquitto_publish(mosq, nullptr, topic.c_str(), message.size(), message.c_str(), 0, false);
    if (ret != MOSQ_ERR_SUCCESS) {
        std::cerr << "Failed to publish message: " << mosquitto_strerror(ret) << std::endl;
        return false;
    }
    return true;
}

void MQTTHandler::subscribe(const std::string& topic) {
    int ret = mosquitto_subscribe(mosq, nullptr, topic.c_str(), 0);
    if (ret != MOSQ_ERR_SUCCESS) {
        std::cerr << "Failed to subscribe to topic: " << mosquitto_strerror(ret) << std::endl;
    }
}

struct mosquitto* MQTTHandler::get_mosq() const {
    return mosq;
}
