#include "mqttrespmessage.h"

using json = nlohmann::json;

MQTTRespMessage::MQTTRespMessage(const std::string &topic,
                                 IResponse& response,
                                 const std::string &device,
                                 const std::string &clientResponse,
                                 int serverReceivedTimestamp):
    MQTTMessage(topic, device, clientResponse),
    response(response),
    serverTimestamp(serverReceivedTimestamp){}

json MQTTRespMessage::toJSON() const {
    json message = MQTTMessage::toJSON();
    message["response"] = response.toString();
    message["server_received_timestamp"] = std::string{static_cast<char>(serverTimestamp)};
    return message;
}

std::string MQTTRespMessage::toString() const {
    std::ostringstream oss;
    oss << "MQTTMessage(topic=" << topic;
    oss << ", Response = {" << response.toString();
    oss << "}, device=" << device
        << ", server_timestamp=" << serverTimestamp
        << ", client_response=" << clientResponse
        << ")";

    return oss.str();
}
