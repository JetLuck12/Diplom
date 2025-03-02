#pragma once

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

std::unique_ptr<DeviceInterface> create_mock_device();

class MockLcard : public DeviceInterface {
private:
    std::atomic<bool> running;
    std::mutex data_mutex;
    std::condition_variable data_cv;
    std::queue<float> data_queue;
    std::default_random_engine generator;
    std::uniform_real_distribution<float> distribution;

    void generate_data();

public:
    MockLcard();
    ~MockLcard();
    bool init() override;
    void start() override;
    void stop() override;
    float get_data() override;
};

