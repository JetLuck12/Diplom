#ifndef DATARESPONSE_H
#define DATARESPONSE_H

#include "IResponse.h"
#include <map>
#include "json.hpp"
#include <string>

using json = nlohmann::json;

class DataResponse : public IResponse
{
public:
    DataResponse(const std::string& type) : type_(type), data_(std::map<std::string, double>{}){};
    DataResponse(const std::string& type, std::map<std::string, double> data){
        type_ = type;
        data_ = data;
    }
    json toJson() const override {
        return json(data_);
    }

    std::string toString() const override {
        json obj;
        obj["data"] = data_;
        obj["type"] = type_;
        return obj.dump();
    }
private:
    std::string type_;
    std::map<std::string, double> data_;
};

#endif // DATARESPONSE_H
