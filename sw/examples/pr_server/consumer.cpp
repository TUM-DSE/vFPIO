#include <thread>
#include "queue.hpp"
#include "consumer.h"
#include "printer.h"

using namespace std;

void Consumer::loop() {
    try {
        while (1) {
            Task task = queue->take();
            Printer(vfid) << "Consumer #" << vfid << " process task for clientPid=" << task.clientPid << endl;
            executor.exec(task);
        }
    } catch (std::runtime_error &e) {
        Printer(vfid) << "runtime_error: "<<e.what()<<endl;
    }
}

Consumer::Consumer(int vfid, Queue<Task> *queue):
        vfid(vfid),
        queue(queue),
        executor(vfid)
{
    Printer(vfid)<<"Consumer started, vfid="<<vfid<<endl;
    looper = std::thread([&]() { this->loop(); });
}

Consumer::~Consumer() {
    Printer(vfid)<<"Consumer::~Consumer"<<endl;
}

void Consumer::join() {
    looper.join();
}