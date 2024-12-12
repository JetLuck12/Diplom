#ifndef LCARDDEVICEH_H
#define LCARDDEVICEH_H
#include "DeviceInterface.h"
#include "Lcard_packs/include/ltrapi.h"
#include "Lcard_packs/include/ltr114api.h"

PTLTR114 init_photodiod();
float get_ltr_data(TLTR114* ltr);

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


std::unique_ptr<DeviceInterface> create_real_device() {
    return std::make_unique<LcardDevice>();
}

#endif // LCARDDEVICEH_H
