#include "mqttcmdmessage.h"

MQTTCmdMessage::MQTTCmdMessage(const std::string &topic,
                               const std::string& command,
                               const std::map<std::string, std::string>& params,
                               const std::string &device,
                               const std::string &serverTimestamp,
                               const std::string &clientResponse)
    : MQTTMessage(topic, device, clientResponse),
    command(command),
    params(params),
    serverTimestamp(serverTimestamp),
    clientResponse(clientResponse){}

json MQTTCmdMessage::toJSON() const  {
    json message = ((MQTTMessage*)(this))->toJSON();
    message["command"] = command;
    message["server_timestamp"] = std::string{serverTimestamp};
    message["client_response"] = std::string{clientResponse};
    return message;
}

std::string MQTTCmdMessage::toString() const {
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
        << ")";

    return oss.str();
}

MQTTCmdMessage MQTTCmdMessage::fromJson(const std::string& topic, const std::string& jsonData){
    try {
        auto good_data = "(" + jsonData + ")";
        auto data = json::parse(jsonData);
        std::map<std::string, std::string> params;
        if(data.contains("params") && data["params"].is_object()){
            params = data["params"];
        }
        return MQTTCmdMessage(
            topic,
            data.at("command"),
            params,
            data.at("device"),
            data.at("server_timestamp")
            );
    } catch (const std::exception &e) {
        throw std::runtime_error(std::string("JSON parsing error: ") + e.what());
    }
}

std::string MQTTCmdMessage::getCommand() const
{
    return command;
}

std::map<std::string, std::string> MQTTCmdMessage::getParams() const
{
    return params;
}

