#pragma once

#include "DeviceInterface.h"
#include "ltr114api.h"
#include <memory>

void init_photodiod(TLTR114* pltr);
float get_ltr_data(TLTR114* ltr);

std::unique_ptr<DeviceInterface> create_real_device();

class LcardDevice : public DeviceInterface {
private:
    TLTR114* ltr; // Указатель на реальное устройство

public:
    LcardDevice();
    ~LcardDevice(){
        delete ltr;
    }

    // Инициализация устройства
    bool init() override;

    // Запуск устройства
    void start() override;

    // Получение данных с устройства
    float get_data() override;

    // Остановка устройства
    void stop() override;
};

