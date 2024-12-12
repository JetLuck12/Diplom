#ifndef DEVICEINTERFACE_H
#define DEVICEINTERFACE_H

#include <iostream>
#include <memory> // Для std::unique_ptr

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

#endif // DEVICEINTERFACE_H
