#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <vector>
#include <chrono>

#include "cProcess.hpp"

using namespace fpga;

using namespace std;
using namespace std::chrono;

// Number of addresses i.e. total of 64KiB
constexpr auto const bram_size = 1024;

constexpr auto const ddefSize = 64;

uint32_t
permute(uint32_t idx)
{
    uint64_t prime = (1 << 19) - 1;
    uint64_t temp = idx;
    temp = (temp * temp) & 0x3FFFFFFFFF;
    temp = temp % prime;
    temp = (idx & (1 << 18)) ? prime - temp : temp;
    return temp;
}

int main(int argc, char *argv[])
{
    uint64_t *fMem;
    uint64_t n_pages = ddefSize / hugePageSize + ((ddefSize % hugePageSize > 0) ? 1 : 0);
    cProcess cproc(0, getpid());

    fMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_pages});
    cproc.ioSwDbg();
    // cproc.ioSwitch(IODevs::HOST_MEM);
    cproc.ioSwitch(IODevs::FPGA_DRAM);
    cproc.ioSwDbg();

    // Write data to FPGA DRAM
    cproc.invoke({CoyoteOper::OFFLOAD, (void *)fMem, 8, true, true, 0, false});
    cproc.invoke({CoyoteOper::READ, (void *)fMem, 8, true, true, 0, false});
    cproc.invoke({CoyoteOper::WRITE, (void *)fMem, 8, true, true, 0, false});
    cproc.invoke({CoyoteOper::SYNC, (void *)fMem, 8, true, true, 0, false});

    high_resolution_clock::time_point start, end;
    start = high_resolution_clock::now();
    for (uint64_t i = 0; i < 65536; ++i)
    {
        uint64_t rng = permute(permute(i) ^ 0x3635) / bram_size;
        memcpy(fMem, &rng, 8);
        // cproc.invoke({CoyoteOper::TRANSFER, (void *)fMem, (void *)fMem, 8, ddefSize});

        cproc.invoke({CoyoteOper::OFFLOAD, (void *)fMem, 8, true, true, 0, false});
        cproc.invoke({CoyoteOper::READ, (void *)fMem, 8, true, true, 0, false});
        cproc.invoke({CoyoteOper::WRITE, (void *)fMem, 64, true, true, 0, false});
        cproc.invoke({CoyoteOper::SYNC, (void *)fMem, 64, true, true, 0, false});
        // std::cout << "fMem:" << *((uint64_t *)fMem) << std::endl;
        // std::cout << "Generated rng value: " << rng / bram_size << std::endl;
    }
    end = high_resolution_clock::now();

    duration<double> diff = end - start;
    double time = duration_cast<std::chrono::microseconds>(end - start).count();
    std::cout << "time: " << time << " us" << std::endl;

    double seconds = diff.count();
    double throughput = ((double)(ddefSize * 65536)) / seconds / (1 << 20);
    printf("cpu rng: %d bytes in %g seconds for %g MiB/s\n", ddefSize * 65536, seconds, throughput);

    return 0;
}