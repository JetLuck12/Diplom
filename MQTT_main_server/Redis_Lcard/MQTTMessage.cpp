#include "MQTTMessage.h"
#include <sstream>

MQTTMessage::MQTTMessage(const std::string &topic,
                         const std::string &command,
                         const std::map<std::string, std::string> &params,
                         const std::string &device,
                         double serverTimestamp,
                         const std::string &clientResponse,
                         double serverReceivedTimestamp)
    : topic(topic),
    command(command),
    params(params),
    device(device),
    serverTimestamp(serverTimestamp),
    clientResponse(clientResponse),
    serverReceivedTimestamp(serverReceivedTimestamp) {}

std::string MQTTMessage::toJSON() const {
    json message = {
        {"command", command},
        {"params", params},
        {"device", device},
        {"server_timestamp", serverTimestamp},
        {"client_response", clientResponse},
        {"server_received_timestamp", serverReceivedTimestamp}
    };
    return message.dump();
}

void MQTTMessage::publish(MQTTHandler &mqttClient) const {
    mqttClient.publish(topic, toJSON());
}

MQTTMessage MQTTMessage::fromJSON(const std::string &topic, const std::string &jsonData) {
    try {
        auto data = json::parse(jsonData);
        return MQTTMessage(
            topic,
            data.at("command").get<std::string>(),
            data.value("params", std::map<std::string, std::string>{}),
            data.value("device", ""),
            data.value("server_timestamp", std::time(nullptr)),
            data.value("client_response", ""),
            data.value("server_received_timestamp", 0.0)
            );
    } catch (const std::exception &e) {
        throw std::runtime_error(std::string("JSON parsing error: ") + e.what());
    }
}

void MQTTMessage::setClientResponse(const std::string &response, double serverReceivedTimestamp) {
    clientResponse = response;
    this->serverReceivedTimestamp = serverReceivedTimestamp;
}

std::string MQTTMessage::toString() const {
    std::ostringstream oss;
    oss << "MQTTMessage(topic=" << topic
        << ", command=" << command
        << ", params={";

    for (const auto &[key, value] : params) {
        oss << key << ":" << value << ", ";
    }

    oss << "}, device=" << device
        << ", server_timestamp=" << serverTimestamp
        << ", client_response=" << clientResponse
        << ", server_received_timestamp=" << serverReceivedTimestamp
        << ")";

    return oss.str();
}
