#pragma once

#include "task.h"
#include "reconfig.h"

class Executor {
    int vfid;
    map<int,int> operatorMap;
    Reconfig reconfig;
    int programmed_op = -1;

public:
    Executor(int vfid);
    ~Executor();

    void exec(const Task &task);

private:
    string filename(int config);

};