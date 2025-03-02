#ifndef MQTTMESSAGE_H
#define MQTTMESSAGE_H

#include <string>
#include <map>
#include <ctime>
#include "json.hpp"

using json = nlohmann::json;

class MQTTMessage {
public:
    MQTTMessage(const std::string &topic,
                const std::string &device = "",
                const std::string &clientResponse = "");

    virtual json toJSON() const;
    static MQTTMessage fromJson(const std::string &topic, const std::string &jsonData);

    void setClientResponse(double serverReceivedTimestamp = std::time(nullptr));

    virtual std::string toString() const;

    virtual std::string getTopic() const;
    virtual std::string getDevice() const;

protected:
    std::string topic;
    std::string device;
    std::string clientResponse;
};

#endif // MQTTMESSAGE_H
