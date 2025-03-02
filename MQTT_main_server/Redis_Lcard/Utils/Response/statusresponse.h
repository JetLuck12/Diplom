#ifndef STATUSRESPONSE_H
#define STATUSRESPONSE_H

#include "IResponse.h"

using json = nlohmann::json;
class StatusResponse : public IResponse
{
public:
    StatusResponse(const std::string& status_) : status(status_){};
    json toJson() const override{
        return json(status);
    }

    std::string toString() const override {
        return status;
    }

private:
    std::string status;
};

#endif // STATUSRESPONSE_H
