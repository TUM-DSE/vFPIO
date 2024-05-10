#include <mutex>
#include <iostream>

#include "printer.h"

std::mutex Printer::mtx_{};

Printer::Printer(int prefix)
        : prefix(std::to_string(prefix))
{
}

Printer::~Printer() {
    std::lock_guard<std::mutex> guard(mtx_);
    if (prefix.empty())
        std::cout << this->str();
    else
        std::cout << "[" << prefix << "] " << this->str();
    std::cout.flush();
}


