#include <mosquitto.h>
#include <string>
#include <functional>
#include <iostream>
#include "mqtthandler.h"

MQTTHandler::MQTTHandler(const std::string& broker_address, int port)
    : mosq(nullptr), broker_address(broker_address), port(port) {
    mosquitto_lib_init();
    mosq = mosquitto_new(nullptr, true, this);
    if (!mosq) {
        throw std::runtime_error("Failed to create mosquitto instance.");
    }
}

MQTTHandler::~MQTTHandler() {
    if (mosq) {
        mosquitto_destroy(mosq);
    }
    mosquitto_lib_cleanup();
}

bool MQTTHandler::connect() {
    if (mosquitto_connect(mosq, broker_address.c_str(), port, 60) != MOSQ_ERR_SUCCESS) {
        return false;
    }
    mosquitto_loop_start(mosq);
    return true;
}

void MQTTHandler::disconnect() {
    if (mosq) {
        mosquitto_disconnect(mosq);
        mosquitto_loop_stop(mosq, true);
    }
}

bool MQTTHandler::publish(const std::string& topic, const MQTTMessage& message) {
    json jsonMessage = message.toJSON();
    std::string str_msg = jsonMessage.dump();
    int ret = mosquitto_publish(mosq, nullptr, topic.c_str(), str_msg.size(), str_msg.c_str(), 1, false);
    return ret == MOSQ_ERR_SUCCESS;
}

void MQTTHandler::subscribe(const std::string& topic, std::function<void(const std::string&)> callback) {
    subscriptions[topic] = callback;
    mosquitto_message_callback_set(mosq, [](struct mosquitto*, void* userdata, const struct mosquitto_message* msg) {
        auto* handler = static_cast<MQTTHandler*>(userdata);
        std::string topic = msg->topic;
        std::string payload(static_cast<const char*>(msg->payload), msg->payloadlen);

        if (handler->subscriptions.count(topic)) {
            handler->subscriptions[topic](payload);
        }
    });
    mosquitto_subscribe(mosq, nullptr, topic.c_str(), 1);
}

struct mosquitto* MQTTHandler::get_mosq() const {
    return mosq;
}
