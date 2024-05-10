#pragma once

#include <string>
#include <map>
#include <iostream>
#include <fstream>
#include <boost/interprocess/sync/scoped_lock.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <sys/ioctl.h>
#include <linux/ioctl.h>
#include <sys/mman.h>

#include "cDefs.hpp"
#include "printer.h"

enum class CoyoteAlloc {
    REG_4K = 0,
    HUGE_2M = 1,
    HOST_2M = 2,
    RCNFG_2M = 3
};

struct csAlloc {
    // Type
    CoyoteAlloc alloc = { CoyoteAlloc::REG_4K };

    // Number of pages
    uint32_t n_pages = { 0 };
};

class Reconfig {
    using bitstream = std::pair<void*, uint32_t>; // vaddr*, length
    using mappedVal = std::pair<csAlloc, void*>; // n_pages, vaddr_non_aligned

    std::map<int32_t, bitstream> bstreams;
    std::map<void*, mappedVal> mapped_pages;

public:
    Reconfig(int32_t vfid);
    ~Reconfig();

    void addBitstream(std::string, int32_t);
    void removeBitstream(int32_t);
    void reconfigure(int32_t oid);

private:
    int fd;
    uint8_t vfid;
    boost::interprocess::named_mutex plock; // Internal vFPGA lock
    boost::interprocess::named_mutex mlock; // Internal memory lock
    fpga::fCnfg fcnfg;

    uint8_t readByte(std::ifstream &fb)
    {
        char temp;
        fb.read(&temp, 1);
        return (uint8_t)temp;
    }
    void mLock() {
        Printer(vfid)<<"mlock lock"<<std::endl;
        mlock.lock();
        Printer(vfid)<<"mlock acquired"<<std::endl;
    }
    void mUnlock() { mlock.unlock(); }

    void reconfigure(void *vaddr, uint32_t len);
    void *getMemForReconfig(const uint32_t nHugePages);
    void freeMem(void *vaddr);
};
