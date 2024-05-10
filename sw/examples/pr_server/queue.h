#pragma once

#include <deque>
#include <mutex>
#include <condition_variable>

template <typename T>
class Queue
{
    std::deque<T> queue;
    std::mutex mtx;
    std::condition_variable cv;
    bool torndown = false;

public:

    void push(const T &elem);

    T take();

    void teardown();

};