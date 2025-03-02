#include "mqttcmdmessage.h"

MQTTCmdMessage::MQTTCmdMessage(const std::string &topic,
                               const std::string &device,
                               const std::string &clientResponse,
                               double serverReceivedTimestamp)
    : MQTTMessage(topic, device, clientResponse),
    response(response),
    serverTimestamp(serverReceivedTimestamp) {}

std::string MQTTRespMessage::toJSON() const  {
    json message{
        {"device", device},
        {"response", response.toJson()},
        {"server_timestamp", serverTimestamp},
        {"client_response", clientResponse}
    };
    return message.dump();
}

std::string MQTTRespMessage::toString() const {
    {
        std::ostringstream oss;
        oss << "MQTTMessage(topic=" << topic
            << ", response={" << response.toString();

        oss << "}, device=" << device
            << ", client_response=" << clientResponse
            << ")";

        return oss.str();
    }
}

