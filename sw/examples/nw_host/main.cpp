#include <iostream>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <malloc.h>
#include <time.h>
#include <sys/time.h>
#include <chrono>
#include <cstring>
#include <boost/program_options.hpp>


#include "cProcess.hpp"

using namespace fpga;

constexpr auto const ddefSize = 64 * 1024;


void needleman_wunsch(uint64_t (&s0)[32], uint64_t (&s1)[32])
{
    uint64_t dp[32+1][32+1];
    uint64_t match = 0;
    uint64_t max_tmp;

    for (int i = 0; i < 33; i++) {
        dp[0][i] = -i;
        dp[i][0] = -i;
    }

    for (int i = 0; i < 32; i++) {
        for (int j = 0; j < 32; j++) {
            match = (s0[i] == s1[j]) ? 1 : -1;
            if (dp[i][j+1] > dp[i+1][j])
                max_tmp = dp[i][j+1] - 1;
            else
                max_tmp = dp[i+1][j] - 1;
            
            if (dp[i][j] + match > max_tmp)
                max_tmp = dp[i][j] + match;
            dp[i+1][j+1] = max_tmp;
        }
    }
}


int main(int argc, char *argv[])
{
    uint32_t d_data_size = ddefSize;
    uint64_t input_bytes;
    uint64_t output_bytes;
    uint64_t app_bytes;

    uint64_t *aMem;
    uint64_t n_pages;

    n_pages = d_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);


    const uint64_t s_ratio = 512/128;
    const uint64_t sc_ratio = 512/8;
    const uint64_t s0_words = 32;
    const uint64_t s1_words = 32;
    const uint64_t sc_count = s0_words * s_ratio * s1_words * s_ratio;
    const uint64_t sc_words = (sc_count+sc_ratio-1) / sc_ratio;

    uint64_t s0_array[s0_words * 64];
    uint64_t s1_array[s1_words * 64];
    uint64_t s0[32];
    uint64_t s1[32];

    std::cout << "sc_count: " << sc_count << std::endl;
    std::cout << "sc_words: " << sc_words << std::endl;
    
    assert((s0_words+s1_words+1)*64 < d_data_size);
    assert(sc_words*64 < d_data_size);
    
    cProcess cproc(0, getpid());
    aMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HOST_2M, (uint32_t)n_pages});
    ((uint64_t*)aMem)[0] = s0_words;
    ((uint64_t*)aMem)[1] = s1_words;
    ((uint64_t*)aMem)[2] = sc_count;
    ((uint64_t*)aMem)[3] = sc_words;
    
    for(uint32_t i=0; i<s0_words+s1_words; i++)
        for(uint32_t j=0; j<64; j++)
            ((uint64_t*)aMem)[(i+1)*64+j] = (i*31+j*37)%251;
    
    input_bytes = (s0_words+s1_words+1)*64;
    output_bytes = sc_words*64;

    cproc.ioSwitch(IODevs::FPGA_DRAM);

    auto start_time = std::chrono::high_resolution_clock::now();

    cproc.invoke({CoyoteOper::OFFLOAD, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::READ, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::WRITE, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::SYNC, (void *)aMem, d_data_size, true, true, 0, false});

    auto start_time_2 = std::chrono::high_resolution_clock::now();

    for (uint64_t i = 0; i < s0_words * 4; i++) {
        for (uint64_t j = 0; j < s1_words * 4; j++) {
            for (uint64_t k = 0; k < 32; k++) {
                s0[k] = s0_array[i*16+k];
                s1[k] = s1_array[j*16+k];
            }
            needleman_wunsch(s0, s1);
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
    double time_2 = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time_2).count();

    app_bytes = (s0_words + s1_words + sc_words) * 64;
    std::cout << "app bytes: " << app_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;
    std::cout << "finished running: " << std::endl;
    std::cout << "time " << time << "us" << std::endl;
    std::cout << "exec time " << time_2 << "us" << std::endl;
    // 1 / 1024 / 1024 / (10^-6) = 0.9536
    std::cout << "throughput " << app_bytes * 0.9536 / time << " MB/s" << std::endl;
}
