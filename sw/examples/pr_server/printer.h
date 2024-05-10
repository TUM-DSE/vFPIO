#pragma once

#include <sstream>
#include <mutex>
#include <iostream>
#include <utility>

class Printer: public std::ostringstream
{
    std::string prefix;
    static std::mutex mtx_;

public:
    Printer() = default;
    Printer(int);
    ~Printer();
};
