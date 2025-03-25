#include "mqttrespmessage.h"

using json = nlohmann::json;

MQTTRespMessage::MQTTRespMessage(const std::string &topic,
                                 IResponse& response,
                                 const std::string &device,
                                 const std::string &time):
    MQTTMessage(topic, device, time),
    response(response){}

json MQTTRespMessage::toJSON() const {
    json message = MQTTMessage::toJSON();
    message["response"] = response.toString();
    message["time"] = time;
    return message;
}

std::string MQTTRespMessage::toString() const {
    std::ostringstream oss;
    oss << "MQTTMessage(topic=" << topic;
    oss << ", Response = {" << response.toString();
    oss << "}, device=" << device
        << ", time=" << time
        << ")";

    return oss.str();
}
