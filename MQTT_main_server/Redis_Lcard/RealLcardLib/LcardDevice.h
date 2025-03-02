#pragma once

#include "DeviceInterface.h"
#include "ltr114api.h"
#include <memory>

PTLTR114 init_photodiod();
float get_ltr_data(TLTR114* ltr);

std::unique_ptr<DeviceInterface> create_real_device();

class LcardDevice : public DeviceInterface {
private:
    PTLTR114 ltr; // Указатель на реальное устройство

public:
    LcardDevice();

    // Инициализация устройства
    bool init() override;

    // Запуск устройства
    void start() override;

    // Получение данных с устройства
    float get_data() override;

    // Остановка устройства
    void stop() override;
};

