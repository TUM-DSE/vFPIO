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

/**
 * @brief Main
 *
 */
int main(int argc, char *argv[])
{
    IODevs dev = IODevs::HOST_MEM;
    uint32_t d_data_size = 1024;
    uint32_t o_data_size = 1024;
    uint64_t *fMem;
    uint64_t n_in_pages, n_out_pages;
    n_in_pages = d_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);
    n_out_pages = o_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);
    cProcess cproc(0, getpid());
    fMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_in_pages});

    if (dev == IODevs::HOST_MEM)
    {
        cproc.ioSwitch(IODevs::HOST_MEM);
        cproc.invoke({CoyoteOper::TRANSFER, (void *)fMem, (void *)fMem, d_data_size, o_data_size});
    }
    else if (dev == IODevs::FPGA_DRAM)
    {
        cproc.ioSwitch(IODevs::FPGA_DRAM);
        cproc.invoke({CoyoteOper::OFFLOAD, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::READ, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::WRITE, (void *)fMem, d_data_size, true, true, 0, false});
        cproc.invoke({CoyoteOper::SYNC, (void *)fMem, o_data_size, true, true, 0, false});
    }
}