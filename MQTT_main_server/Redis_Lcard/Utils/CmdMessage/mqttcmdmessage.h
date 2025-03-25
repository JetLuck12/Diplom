#ifndef MQTTCMDMESSAGE_H
#define MQTTCMDMESSAGE_H

#include "MQTTMessage.h"

using json = nlohmann::json;

class MQTTCmdMessage : public MQTTMessage
{
public:
    MQTTCmdMessage(const std::string &topic,
                   const std::string& command,
                   const std::map<std::string, std::string>& params,
                   const std::string &device = "",
                   const std::string &time = {});

    json toJSON() const override;
    std::string toString() const override;

    static MQTTCmdMessage fromJson(const std::string& topic, const std::string& jsonData);

    std::string getCommand() const;

    std::map<std::string, std::string> getParams() const;

private:
    std::string command;
    std::map<std::string, std::string> params;
};

#endif // MQTTCMDMESSAGE_H
