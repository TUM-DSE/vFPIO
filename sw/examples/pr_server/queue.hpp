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

    void push(const T &elem) {
        std::lock_guard<std::mutex> lock(mtx);
        queue.push_back(elem);
        cv.notify_all();
    }

    T take() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&]() { return !queue.empty() || torndown; });
        if(torndown) {
            throw std::runtime_error("Queue is tearing down");
        }
        T elem = queue.front();
        queue.pop_front();
        return elem;
    }

    void teardown() {
        std::lock_guard<std::mutex> lock(mtx);
        // after teardown, the take() function must not return any more elements,
        // as the calling object may have been destructed
        torndown = true;
        cv.notify_all();
    }

};