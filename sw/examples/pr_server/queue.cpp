#include <mutex>

#include "task.h"
#include "queue.h"

template<typename T>
void Queue<T>::push(const T &elem) {
    std::lock_guard<std::mutex> lock(mtx);
    queue.push_back(elem);
    cv.notify_all();
}

template<typename T>
T Queue<T>::take() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&]() { return !queue.empty() || torndown; });
    if(torndown) {
        throw std::runtime_error("Queue is tearing down");
    }
    Task elem = queue.front();
    queue.pop_front();
    return elem;
}

template<typename T>
void Queue<T>::teardown() {
    std::lock_guard<std::mutex> lock(mtx);
    // after teardown, the take() function must not return any more elements,
    // as the calling object may have been destructed
    torndown = true;
    cv.notify_all();
}
