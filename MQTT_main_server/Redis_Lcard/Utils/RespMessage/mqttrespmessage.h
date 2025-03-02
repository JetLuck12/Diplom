#ifndef MQTTRESPMESSAGE_H
#define MQTTRESPMESSAGE_H

#include "MQTTMessage.h"
#include "Response/IResponse.h"

using json = nlohmann::json;

class MQTTRespMessage : public MQTTMessage
{
public:
    MQTTRespMessage(const std::string &topic,
                   IResponse& response,
                   const std::string &device = "",
                   const std::string &clientResponse = "",
                   int serverReceivedTimestamp = 0.0);

    json toJSON() const override;
    std::string toString() const override;

private:
    IResponse& response;
    int serverTimestamp;
};

#endif // MQTTRESPMESSAGE_H
