#include "MQTTMessage.h"
#include <sstream>

MQTTMessage::MQTTMessage(const std::string &topic,
                         const std::string &device,
                         const std::string &clientResponse)
    : topic(topic),
    device(device),
    time(time) {}

json MQTTMessage::toJSON() const {
    json message = {
        {"topic", topic},
        {"device", device},
        {"time", time}
    };
    return message;
}

MQTTMessage MQTTMessage::fromJson(const std::string &topic, const std::string &jsonData) {
    try {
        auto data = json::parse(jsonData);
        return MQTTMessage(
            topic,
            data.value("device", ""),
            data.value("client_response", "")
            );
    } catch (const std::exception &e) {
        throw std::runtime_error(std::string("JSON parsing error: ") + e.what());
    }
}

void MQTTMessage::setClientResponse(std::string serverReceivedTimestamp) {
    this->time = serverReceivedTimestamp;
}

std::string MQTTMessage::toString() const {
    std::ostringstream oss;
    oss << "MQTTMessage(topic=" << topic
        << ", device=" << device
        << ", client_response=" << time
        << ")";

    return oss.str();
}

std::string MQTTMessage::getTopic() const
{
    return topic;
}

std::string MQTTMessage::getDevice() const
{
    return device;
}
