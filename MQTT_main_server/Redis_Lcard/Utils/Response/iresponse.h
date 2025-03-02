#ifndef IRESPONSE_H
#define IRESPONSE_H

#include "json.hpp"

class IResponse {
public:
    virtual nlohmann::json toJson() const = 0;
    virtual std::string toString() const = 0;
};

#endif // IRESPONSE_H
