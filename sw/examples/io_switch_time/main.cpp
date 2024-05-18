#include <iostream>
#include <string>
#include <malloc.h>
#include <time.h> 
#include <sys/time.h>  
#include <chrono>
#include <fstream>
#include <fcntl.h>
#include <unistd.h>
#include <iomanip>
#include <x86intrin.h>
#include <boost/program_options.hpp>
#include <sys/socket.h>
#include <sys/un.h>
#include <sstream>

#include "cLib.hpp"
#include "cProcess.hpp"

using namespace std;
using namespace fpga;

#define SIZE  64 * 1024
#define ALIGNMENT 64
char memUnaligned[SIZE+ALIGNMENT];
int hls4ml_samples = 0;

constexpr auto const defHuge = false;
constexpr auto const defvIO = false;

// Runtime
// constexpr auto const defSize = 8 * 1024;
constexpr auto const defSize = SIZE;

constexpr auto const ioDev = IODevs::FPGA_DRAM;


int main(int argc, char *argv[]) 
{
    std::string opId;
    bool huge = defHuge;
    bool vio = defvIO;
    bool fpga_mem = false;

    // Read arguments
    boost::program_options::options_description programDescription("Options:");
    programDescription.add_options()
        ("operator,o", boost::program_options::value<std::string>(&opId), "Operator")
        ("hugepages,h", boost::program_options::bool_switch(&huge), "Hugepages")
        ("vio,i", boost::program_options::bool_switch(&vio), "vIO")
        ("fpga_mem,f", boost::program_options::bool_switch(&fpga_mem), "Use fpga mem or not.")
        ("size,s", boost::program_options::value<uint32_t>(), "Data size");

    boost::program_options::variables_map commandLineArgs;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, programDescription), commandLineArgs);
    boost::program_options::notify(commandLineArgs);

    uint32_t size = defSize;
    // IODevs::FPGA_DRAM;
    // IODevs::HOST_MEM;
    // IODevs io_dev = ioDev;
    IODevs io_dev = IODevs::HOST_MEM;
    uint64_t input_bytes;
    uint64_t output_bytes;
    uint64_t app_bytes;

    if(commandLineArgs.count("size") > 0) size = commandLineArgs["size"].as<uint32_t>();


    if (commandLineArgs.count("size") > 0)
        size = commandLineArgs["size"].as<uint32_t>();
    std::cout << "size " << size << std::endl;
    uint32_t n_pages = huge ? ((size + hugePageSize - 1) / hugePageSize) :
                                ((size + pageSize - 1) / pageSize);
    std::cout << "n_pages: " << n_pages << std::endl;
    cProcess cproc(0, getpid());
 
    // get memory pointer
    void *mem = (uint64_t *)cproc.getMem({huge ? CoyoteAlloc::HUGE_2M : CoyoteAlloc::REG_4K, (uint32_t)n_pages});

    // void *mem = memUnaligned + ALIGNMENT - ((int64_t)memUnaligned)%ALIGNMENT;
    // cproc.userMap((void *) mem, size);

    uint64_t io_status = 0;
    uint64_t io_target = 0;
    // IO device: use host memory
    
    for (int i = 0; i < 5; i++) {
        cproc.ioSwDbg();
        io_dev = IODevs::FPGA_DRAM;
        io_target = 0x02;

        auto io_start_time = std::chrono::high_resolution_clock::now();
        // io_dev = ioDev;
        cproc.ioSwitch(io_dev);
        // cproc.ioSwDbg();

        while (io_status != io_target){
            io_status = cproc.ioStatus();
            // std::cout << io_status << std::endl;
        }
        auto io_end_time = std::chrono::high_resolution_clock::now();
        double io_time = std::chrono::duration_cast<std::chrono::nanoseconds>(io_end_time - io_start_time).count();
        std::cout << "io_time " << io_time/1000 << " us" << std::endl;

        io_dev = IODevs::HOST_MEM;
        io_target = 0x01;

        io_start_time = std::chrono::high_resolution_clock::now();
        // io_dev = ioDev;
        cproc.ioSwitch(io_dev);
        // cproc.ioSwDbg();

        while (io_status != io_target){
            io_status = cproc.ioStatus();
            // std::cout << io_status << std::endl;
        }
        io_end_time = std::chrono::high_resolution_clock::now();
        io_time = std::chrono::duration_cast<std::chrono::nanoseconds>(io_end_time - io_start_time).count();

        cproc.ioSwDbg();
        std::cout << "io_time " << io_time/1000 << " us" << std::endl;

    }
    return (EXIT_SUCCESS);
}
