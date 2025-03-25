#ifndef MQTTRESPMESSAGE_H
#define MQTTRESPMESSAGE_H

#include "MQTTMessage.h"
#include "Response/IResponse.h"

#include <ctime>

using json = nlohmann::json;

class MQTTRespMessage : public MQTTMessage
{
public:
    MQTTRespMessage(const std::string &topic,
                   IResponse& response,
                   const std::string &device = "",
                    const std::string &time = std::to_string(std::time(nullptr)));

    json toJSON() const override;
    std::string toString() const override;

private:
    IResponse& response;
};

#endif // MQTTRESPMESSAGE_H
