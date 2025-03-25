#include "mqttcmdmessage.h"

MQTTCmdMessage::MQTTCmdMessage(const std::string &topic,
                               const std::string& command,
                               const std::map<std::string, std::string>& params,
                               const std::string &device,
                               const std::string &time)
    : MQTTMessage(topic, device, time),
    command(command),
    params(params){}

json MQTTCmdMessage::toJSON() const  {
    json message = ((MQTTMessage*)(this))->toJSON();
    message["command"] = command;
    message["time"] = time;
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
        << ", time=" << time
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
        std::string command = data.at("command");
        std::string device = data.at("device");
        int time = data.at("time");
        return MQTTCmdMessage(
            topic,
            command,
            params,
            device,
            std::to_string(time)
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

