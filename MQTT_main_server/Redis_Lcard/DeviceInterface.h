#pragma once
#include <memory>

// Интерфейс устройства
class DeviceInterface {
public:
    virtual ~DeviceInterface() = default;

    // Метод инициализации
    virtual bool init() = 0;

    // Метод для запуска устройства
    virtual void start() = 0;

    // Метод для получения данных
    virtual float get_data() = 0;

    // Метод для остановки устройства
    virtual void stop() = 0;
};

std::unique_ptr<DeviceInterface> create_mock_device(); // Only declaration
std::unique_ptr<DeviceInterface> create_real_device();

