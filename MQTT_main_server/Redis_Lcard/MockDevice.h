#ifndef MOCKDEVICE_H
#define MOCKDEVICE_H

#include <iostream>
#include <vector>
#include <string>
#include <thread>
#include <chrono>
#include <random>
#include <atomic>
#include <queue>
#include <mutex>
#include <condition_variable>
#include "DeviceInterface.h"

class MockLcard : public DeviceInterface {
private:
    std::atomic<bool> running;                  // Состояние фотодиода
    std::mutex data_mutex;                      // Мьютекс для управления доступом к данным
    std::condition_variable data_cv;           // Условная переменная для уведомления о новых данных
    std::queue<float> data_queue;              // Очередь данных
    std::default_random_engine generator;      // Генератор случайных чисел
    std::uniform_real_distribution<float> distribution; // Диапазон для генерации данных

    void generate_data();

public:
    MockLcard();
    ~MockLcard();
    bool init() override;
    void start() override;
    void stop() override;
    float get_data() override;
};

// Функция для создания имитационного устройства
std::unique_ptr<DeviceInterface> create_mock_device() {
    // Используем заранее написанный класс MockDevice
    return std::make_unique<MockLcard>();
}

#endif // MOCKDEVICE_H
