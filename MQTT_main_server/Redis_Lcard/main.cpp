#include <iostream>
#include "MockDevice.h"
#include "DeviceInterface.h"
#include "LcardDevice.h"



// Реализация create_device
// Эта функция предполагает, что классы MockDevice и RealDevice уже написаны
std::unique_ptr<DeviceInterface> create_device(bool test_flag) {
    if (test_flag) {
        // Возвращаем экземпляр имитационного устройства
        return std::unique_ptr<DeviceInterface>(create_mock_device());
    } else {
        // Возвращаем экземпляр реального устройства
        return std::unique_ptr<DeviceInterface>(create_real_device());
    }
}

int main() {
    bool test_flag = true; // Флаг: true для имитационного устройства, false для реального

    // Выбор устройства в зависимости от test_flag
    std::unique_ptr<DeviceInterface> device = create_device(test_flag);

    // Инициализация устройства
    if (!device->init()) {
        std::cerr << "Failed to initialize device.\n";
        return 1;
    }

    // Запуск устройства
    device->start();

    // Чтение данных
    for (int i = 0; i < 10; ++i) {
        float data = device->get_data();
        std::cout << "Received data: " << data << '\n';
    }

    // Остановка устройства
    device->stop();

    return 0;
}

