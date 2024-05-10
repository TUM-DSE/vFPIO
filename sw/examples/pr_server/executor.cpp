#include "executor.h"
#include "task.h"
#include "reconfig.h"
#include "cProcess.hpp"
#include "printer.h"
// #include "metrics.h"

string Executor::filename(int config) {
    char* envdir = getenv("BITSTREAM_DIR");
    char* homedir = getenv("HOME");
    std::string name = "part_bstream_c" + to_string(config) + "_" + to_string(vfid) + ".bin";
    if(envdir!=NULL) {
        return string(envdir) + "/" + name;
    } else if (homedir!=NULL) {
        return string(homedir) + "/bitstreams/" + name;
    } else {
        return name;
    }
}

Executor::Executor(int vfid) :
        vfid(vfid),
        reconfig(vfid) {
}

Executor::~Executor() {
    cerr<<"Executor::~Executor"<<endl;
}

void Executor::exec(const Task &task) {
    TaskStats stats(task, vfid);
    stats.launch_time = std::chrono::system_clock::now();

    //TODO measure reconfig time correctly

    int opId;
    if (operatorMap.count(task.bitstreamConfig)) {
        cerr << "reuse operator" << endl;
        opId = operatorMap[task.bitstreamConfig];
        stats.bitstream_added = false;
    } else {
        cerr << "add operator" << endl;
        opId = operatorMap[task.bitstreamConfig] = operatorMap.size() + 1;
        cerr << "filename=" << filename(task.bitstreamConfig) << endl;
        reconfig.addBitstream(filename(task.bitstreamConfig), opId);
        stats.bitstream_added = true;
    }

    fpga::cProcess cproc(vfid, task.clientPid);

    Printer(vfid) << "locking" << endl;
    cproc.pLock(opId, 0);

    if(opId == programmed_op) {
        Printer(vfid) << "reconfiguration not necessary" << endl;
        stats.reconfig_performed = false;
    } else {
        Printer(vfid) << "reconfiguration " << opId << endl;
        reconfig.reconfigure(opId);
        programmed_op = opId;
        stats.reconfig_performed = true;
        stats.reconfigured_time = std::chrono::system_clock::now();
    }

    // Printer(vfid) << "set csr's" << endl;
    // for (auto &csr: task.csrMap) {
    //     cproc.setCSR(csr.second, csr.first);
    // }

    // for (auto &mem: task.mappedMem) {
    //     Printer(vfid) << "cproc.userMap, hMemAddr=" << hex << mem.first << dec << ", hMemSize=" << mem.second << endl;
    //     cproc.userMap((void *) mem.first, mem.second);
    // }

    // Printer(vfid) << "cproc.invoke" << endl;
    // cproc.invoke({fpga::CoyoteOper::TRANSFER, (void *) task.inputMem.first, (void *) task.outputMem.first,
    //               task.inputMem.second, task.outputMem.second});

    // for (auto &mem: task.mappedMem) {
    //     Printer(vfid) << "unmap, hMemAddr=" << hex << mem.first << dec << ", hMemSize=" << mem.second << endl;
    //     cproc.userUnmap((void *) mem.first);
    // }

    Printer(vfid) << "unlock" << endl;
    cproc.pUnlock();

    stats.completion_time = std::chrono::system_clock::now();
    // Metrics::push(stats);

    char msg[4096] = {'O', 'K', 0};
    if (write(task.clientFd, msg, 4096) == -1) {
        perror("write");
    }

    /*if(close(task.clientFd) == -1) {
        perror("close");
    }*/
}
