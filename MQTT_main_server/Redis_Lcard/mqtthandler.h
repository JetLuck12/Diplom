#pragma once
#include <mosquitto.h>
#include <string>

class MQTTHandler {
public:
    MQTTHandler(const std::string& broker_address, int port);
    ~MQTTHandler();

    bool connect();
    void disconnect();

    bool publish(const std::string& topic, const std::string& message);
    void subscribe(const std::string& topic);

    struct mosquitto* get_mosq() const;
private:
    struct mosquitto* mosq;
    std::string broker_address;
    int port;
};
