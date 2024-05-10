#pragma once

#include <thread>
#include <string>
#include <map>

#include "queue.hpp"
#include "executor.h"
#include "task.h"

class Consumer {

    int vfid;
    Queue<Task> *queue;
    Executor executor;

    std::map<std::string,int32_t> operatorMap;
    std::thread looper;

    void loop();

public:
    Consumer(int vfid, Queue<Task> *queue);
    ~Consumer();

    void join();

};