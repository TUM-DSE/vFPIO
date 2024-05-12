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
#ifdef EN_AVX
#include <x86intrin.h>
#endif
#include <boost/program_options.hpp>

#include "cBench.hpp"
#include "cProcess.hpp"

using namespace std;
using namespace fpga;

/* Def params */
constexpr auto const nRegions = 3;
constexpr auto const defHuge = false;
constexpr auto const defMappped = true;
constexpr auto const nReps = 1000;
constexpr auto const defMinSize = 16 * 1024;
constexpr auto const defMaxSize = 16 * 1024;
constexpr auto const nBenchRuns = 3;
constexpr auto const defSkip = -1;

/**
 * @brief Loopback example
 * 
 */
int main(int argc, char *argv[])  
{
    // ---------------------------------------------------------------
    // Args 
    // ---------------------------------------------------------------

    // Read arguments
    boost::program_options::options_description programDescription("Options:");
    programDescription.add_options()
        ("regions,n", boost::program_options::value<uint32_t>(), "Number of vFPGAs")
        ("hugepages,h", boost::program_options::value<bool>(), "Hugepages")
        ("mapped,m", boost::program_options::value<bool>(), "Mapped / page fault")
        ("reps,r", boost::program_options::value<uint32_t>(), "Number of repetitions")
        ("min_size,s", boost::program_options::value<uint32_t>(), "Starting transfer size")
        ("max_size,e", boost::program_options::value<uint32_t>(), "Ending transfer size")
        ("skip_region,k", boost::program_options::value<uint32_t>(), "Region to skip");
    
    boost::program_options::variables_map commandLineArgs;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, programDescription), commandLineArgs);
    boost::program_options::notify(commandLineArgs);

    uint32_t n_regions = nRegions;
    bool huge = defHuge;
    bool mapped = defMappped;
    uint32_t n_reps = nReps;
    uint32_t curr_size = defMinSize;
    uint32_t max_size = defMaxSize;
    uint32_t skip = defSkip;

    if(commandLineArgs.count("regions") > 0) n_regions = commandLineArgs["regions"].as<uint32_t>();
    if(commandLineArgs.count("hugepages") > 0) huge = commandLineArgs["hugepages"].as<bool>();
    if(commandLineArgs.count("mapped") > 0) mapped = commandLineArgs["mapped"].as<bool>();
    if(commandLineArgs.count("reps") > 0) n_reps = commandLineArgs["reps"].as<uint32_t>();
    if(commandLineArgs.count("min_size") > 0) curr_size = commandLineArgs["min_size"].as<uint32_t>();
    if(commandLineArgs.count("max_size") > 0) max_size = commandLineArgs["max_size"].as<uint32_t>();
    if(commandLineArgs.count("skip_region") > 0) skip = commandLineArgs["skip_region"].as<uint32_t>();

    uint32_t n_pages = huge ? ((max_size + hugePageSize - 1) / hugePageSize) : ((max_size + pageSize - 1) / pageSize);

    PR_HEADER("PARAMS");
    std::cout << "Number of regions: " << n_regions << std::endl;
    std::cout << "Hugepages: " << huge << std::endl;
    std::cout << "Mapped pages: " << mapped << std::endl;
    std::cout << "Number of allocated pages: " << n_pages << std::endl;
    std::cout << "Number of repetitions: " << n_reps << std::endl;
    std::cout << "Starting transfer size: " << curr_size << std::endl;
    std::cout << "Ending transfer size: " << max_size << std::endl;

    // ---------------------------------------------------------------
    // Init 
    // ---------------------------------------------------------------

    // Handles
    std::vector<std::unique_ptr<cProcess>> cproc; // Coyote process
    void* hMem[n_regions];
    
    // Obtain resources
    for (int i = 0; i < n_regions; i++) {
        if (i == skip) {
            cproc.emplace_back(new cProcess(i, getpid()));
            continue;
        }
        cproc.emplace_back(new cProcess(i, getpid()));
        hMem[i] = mapped ? (cproc[i]->getMem({huge ? CoyoteAlloc::HUGE_2M : CoyoteAlloc::REG_4K, n_pages})) 
                         : (huge ? (mmap(NULL, max_size, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0))
                                 : (malloc(max_size)));
    }
    std::cout << "Finished memory mapping" << std::endl;

    // // Fill data
    // for (int i=0; i < n_regions; i++) {
    //     if (i == skip)
    //         continue;
    //     printf("hMem[%d] before: ", i);
    //     for (int j = 0; j < curr_size/4; j++) {
    //         printf("%d ", ((uint32_t*) hMem[i])[j]);
    //     }
    //     printf("\n");
    // }

    // // priority: 3 (11) 2 bits
    // // I/O type: 1 (01) 2 bits
    // // length: 128 (80) 12 bits
    // ((uint32_t*) hMem[0])[0] = 0xffee080D;

    // ---------------------------------------------------------------
    // Runs 
    // ---------------------------------------------------------------
    cBench bench(nBenchRuns);
    uint32_t n_runs;

    PR_HEADER("PERF HOST");
    while(curr_size <= max_size) {
        // Prep
        for(int i = 0; i < n_regions; i++) {
            if (i == skip)
                continue;
            cproc[i]->clearCompleted();
        }
        n_runs = 0;
        
        // Throughput test
        auto benchmark_thr = [&]() {
            bool k = false;
            n_runs++;

            std::vector<double> start(n_regions, 0);
            std::vector<double> end(n_regions, 0);
            auto base_time = std::chrono::high_resolution_clock::now();
            // Transfer the data
            for(int i = 0; i < n_reps; i++)
                for(int j = 0; j < n_regions; j++) {
                    if (j == skip)
                        continue;
                    // set higher priority to vfpga 2
                    if (j == 2)
                        cproc[j]->invoke({CoyoteOper::TRANSFER, hMem[j], hMem[j], curr_size, curr_size, false, false, n_reps * n_runs, 1});
                    else
                        cproc[j]->invoke({CoyoteOper::TRANSFER, hMem[j], hMem[j], curr_size, curr_size, false, false, n_reps * n_runs});

                }
            auto end_time = std::chrono::high_resolution_clock::now();
            double time = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - base_time).count();
            for(int j = 0; j < n_regions; j++) {
                start[j] = time;
            }

            while(!k) {
                k = true;
                for(int i = 0; i < n_regions; i++) {
                    if (i == skip)
                        continue;
                    if(cproc[i]->checkCompleted(CoyoteOper::TRANSFER) != (n_reps * n_runs - 0)) {
                        k = false;
                    }
                    else {
                        if (end[i] > 1) {
                            continue;
                        }
                        end_time = std::chrono::high_resolution_clock::now();
                        time = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - base_time).count();
                        end[i] = time;
                    }
                }
            }
                        end_time = std::chrono::high_resolution_clock::now();
                        time = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - base_time).count();
                        end[0] = time;
            for(int i = 0; i < n_regions; i++) {
                std::cout << "time " << i << " " << (end[i] - start[i]) / n_reps << std::endl;
            }
        };
        bench.runtime(benchmark_thr);
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Average: " << bench.getAvg() << std::endl;
        std::cout << "Lat: " << std::setw(8) << bench.getAvg() / (n_reps) << " ns" << std::endl;
        std::cout << "Size: " << std::setw(8) << curr_size << ", thr: " << std::setw(8) << (n_regions * 1000 * curr_size) / (bench.getAvg() / n_reps) << " MB/s";

        // Latency test
        auto benchmark_lat = [&]() {
            // Transfer the data
            for(int i = 0; i < n_reps; i++) {
                for(int j = 0; j < n_regions; j++) {
                    if (j == skip)
                        continue;
                    cproc[j]->invoke({CoyoteOper::TRANSFER, hMem[j], hMem[j], curr_size, curr_size, true, false});
                    while(cproc[j]->checkCompleted(CoyoteOper::TRANSFER) != 1) ;            
                }
            }
        };
        // bench.runtime(benchmark_lat);
        // std::cout << ", lat: " << std::setw(8) << bench.getAvg() / (n_reps) << " ns" << std::endl;

        curr_size *= 2;
    }
    std::cout << std::endl;
    
    // for (int i=0; i < n_regions; i++) {
    //     if (i == skip)
    //         continue;
    //     printf("hMem[%d] after: ", i);
    //     for (int j = 0; j < curr_size/4/2; j++) {
    //         printf("%d ", ((uint32_t*) hMem[i])[j]);
    //     }
    //     printf("\n");
    // }
    
    // ---------------------------------------------------------------
    // Release 
    // ---------------------------------------------------------------
    
    // Print status
    for (int i = 0; i < n_regions; i++) {
        if (i == skip)
            continue;
        cproc[i]->printDebug();
        if(!mapped) {
            if(!huge) free(hMem[i]);
            else      munmap(hMem[i], max_size);  
        }
    }
    
    return EXIT_SUCCESS;
}
