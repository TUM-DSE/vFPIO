#include <dirent.h>
#include <iterator>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <iostream>
#include <stdlib.h>
#include <string>
#include <sys/stat.h>
#include <syslog.h>
#include <unistd.h>
#include <vector>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <iomanip>
#include <chrono>
#include <thread>
#include <limits>
#include <assert.h>
#include <stdio.h>
#include <sys/un.h>
#include <errno.h>
#include <wait.h>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <condition_variable>
#include <boost/program_options.hpp>

#include "cProcess.hpp"

using namespace std;
using namespace fpga;

uint8_t readByte(ifstream &fb)
{
    char temp;
    fb.read(&temp, 1);
    return (uint8_t)temp;
}

void *getMem(const csAlloc &cs_alloc, cProcess &cproc)
{
    void *mem = nullptr;
    void *memNonAligned = nullptr;
    uint64_t tmp[2];
    uint32_t size;

    if (cs_alloc.n_pages > 0)
    {
        tmp[0] = static_cast<uint64_t>(cs_alloc.n_pages);

        switch (cs_alloc.alloc)
        {
        case CoyoteAlloc::RCNFG_2M: // m lock

            if (ioctl(cproc.getIOctlFD(), IOCTL_ALLOC_HOST_PR_MEM, &tmp))
            {
                throw std::runtime_error("ioctl_alloc_host_pr_mem mapping failed");
            }

            memNonAligned = mmap(NULL, (cs_alloc.n_pages + 1) * hugePageSize, PROT_READ | PROT_WRITE, MAP_SHARED, cproc.getIOctlFD(), mmapPr);
            if (memNonAligned == MAP_FAILED)
            {
                throw std::runtime_error("get_pr_mem mmap failed");
            }

            mem = (void *)((((reinterpret_cast<uint64_t>(memNonAligned) + hugePageSize - 1) >> hugePageShift)) << hugePageShift);

            break;

        default:
            throw std::runtime_error("unauthorized memory allocation, vfid: 0 ");
        }
    }

    return mem;
}

void loadBitstream(std::unordered_map<IODevs, std::pair<void *, uint32_t>> &bstreams, std::string bstrmPath, IODevs dev, cProcess &cproc)
{
    if (bstreams.find(dev) == bstreams.end())
    {
        // Stream
        ifstream f_bit(bstrmPath, ios::ate | ios::binary);
        if (!f_bit)
            throw std::runtime_error("Bitstream could not be opened");

        // Size
        uint32_t len = f_bit.tellg();
        f_bit.seekg(0);
        uint32_t n_pages = (len + hugePageSize - 1) / hugePageSize;

        // Get mem
        void *vaddr = getMem({CoyoteAlloc::RCNFG_2M, n_pages}, cproc);
        uint32_t *vaddr_32 = reinterpret_cast<uint32_t *>(vaddr);

        // Read in
        for (uint32_t i = 0; i < len / 4; i++)
        {
            vaddr_32[i] = 0;
            vaddr_32[i] |= readByte(f_bit) << 24;
            vaddr_32[i] |= readByte(f_bit) << 16;
            vaddr_32[i] |= readByte(f_bit) << 8;
            vaddr_32[i] |= readByte(f_bit);
        }

        f_bit.close();

        bstreams[dev] = std::make_pair(vaddr, len);
        return;
    }

    throw std::runtime_error("bitstream with same operation ID already present");
}

void reconfigFPGA(std::unordered_map<IODevs, std::pair<void *, uint32_t>> &bstreams, IODevs dev, cProcess &cproc)
{
    auto bstream = bstreams[dev];
    void *vaddr = std::get<0>(bstream);
    uint32_t len = std::get<1>(bstream);
    if (cproc.getFcnfg().en_pr)
    {
        uint64_t tmp[2];
        tmp[0] = reinterpret_cast<uint64_t>(vaddr);
        tmp[1] = static_cast<uint64_t>(len);
        if (ioctl(cproc.getIOctlFD(), IOCTL_RECONFIG_LOAD, &tmp)) // Blocking
            throw std::runtime_error("ioctl_reconfig_load failed");
    }
}

/**
 * @brief Main
 *
 */
int main(int argc, char *argv[])
{
    IODevs dev = IODevs::HOST_MEM;

    std::unordered_map<IODevs, std::pair<void *, uint32_t>> bstreams;

    uint32_t d_data_size = 1024;
    uint32_t o_data_size = 1024;
    uint64_t *fMem;
    uint64_t n_in_pages, n_out_pages;
    n_in_pages = d_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);
    n_out_pages = o_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);
    cProcess cproc(0, getpid());
    fMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_in_pages});

    // Read in bitstreams
    if (dev == IODevs::HOST_MEM)
    {
        loadBitstream(bstreams, "part_bstream_c0_0.bin", dev, cproc);
    }
    else if (dev == IODevs::FPGA_DRAM)
    {
        loadBitstream(bstreams, "part_bstream_c1_0.bin", dev, cproc);
    }

    // Reconfigure the FPGA
    reconfigFPGA(bstreams, dev, cproc);

    // Run the UL
    if (dev == IODevs::HOST_MEM)
    {
        cproc.invoke({CoyoteOper::TRANSFER, (void *)fMem, (void *)fMem, d_data_size, o_data_size});
    }
    else if (dev == IODevs::FPGA_DRAM)
    {
        cproc.invoke({CoyoteOper::OFFLOAD, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::READ, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::WRITE, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::SYNC, (void *)fMem, o_data_size, true, true, 0, false});
    }
}