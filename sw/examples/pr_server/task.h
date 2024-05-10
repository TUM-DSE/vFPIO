#pragma once

#include <iostream>
#include <string>
#include <sstream>
#include <map>
#include <vector>
#include <chrono>

using namespace std;

struct Task {
    map<uint32_t, uint64_t> csrMap;
    vector<pair<uint64_t, uint32_t>> mappedMem;
    pair<uint64_t, uint32_t> inputMem;
    pair<uint64_t, uint32_t> outputMem;
    int bitstreamConfig = -1;
    pid_t clientPid = -1;
    int clientFd = -1;
    std::chrono::system_clock::time_point enqueue_time;
};

struct TaskStats {
    std::chrono::system_clock::time_point enqueue_time;
    std::chrono::system_clock::time_point reconfigured_time;
    std::chrono::system_clock::time_point launch_time;
    std::chrono::system_clock::time_point completion_time;
    bool reconfig_performed;
    bool bitstream_added;
    int bitstream_config;
    int used_region;

    TaskStats(const Task &task, int region) :
            enqueue_time(task.enqueue_time),
            bitstream_config(task.bitstreamConfig),
            used_region(region) {
    }
};