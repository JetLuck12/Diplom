#include "mocklcard.h"

void MockLcard::generate_data() {
    // Имитация получения данных
    while (running.load()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(100)); // Задержка для генерации данных
        float simulated_data = distribution(generator);

        {
            std::lock_guard<std::mutex> lock(data_mutex);
            data_queue.push(simulated_data);
        }
        data_cv.notify_one(); // Уведомляем об обновлении данных
    }
}

MockLcard::MockLcard()
    : running(false), distribution(0.0f, 1.0f) {
    std::cout << "MockLcard initialized.\n";
}

MockLcard::~MockLcard() {
    stop();
}

bool MockLcard::init() {
    // Имитация инициализации
    std::cout << "MockLcard initialized successfully.\n";
    return true;
}

void MockLcard::start() {
    // Имитация запуска
    running.store(true);
    std::thread(&MockLcard::generate_data, this).detach();
    std::cout << "MockLcard started.\n";
}

void MockLcard::stop() {
    // Имитация остановки
    running.store(false);
    std::cout << "MockLcard stopped.\n";
}

float MockLcard::get_data() {
    // Имитация получения данных
    std::unique_lock<std::mutex> lock(data_mutex);
    data_cv.wait(lock, [this] { return !data_queue.empty() || !running.load(); });

    if (!data_queue.empty()) {
        float value = data_queue.front();
        data_queue.pop();
        return value;
    }

    return 0.0f; // Возвращаем 0, если данных нет
}

