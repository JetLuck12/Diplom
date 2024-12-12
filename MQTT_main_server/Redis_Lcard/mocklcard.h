#ifndef MOCKLCARD_H
#define MOCKLCARD_H

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

class MockLcard {
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
    bool init();
    void start();
    void stop();
    float get_data();
};

#endif // MOCKLCARD_H
