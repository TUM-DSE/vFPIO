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

#include "cProcess.hpp"

using namespace fpga;

// 8x8 matrix
constexpr auto const nrows = 64;
constexpr auto const ddefSize = nrows * nrows;

void matrixMultiplication(uint64_t *A, uint64_t *B, uint64_t *C, int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            C[i * n + j] = 0;
            for (int n = 0; n < n; n++)
            {
                C[i * n + j] += A[i * n + n] * B[n * n + j];
            }
        }
    }
}

int main(int argc, char *argv[])
{
    uint32_t d_data_size = ddefSize;
    const int MAT_BYTES = 64*64*8;
    int input_bytes = 2 * MAT_BYTES;
    int output_bytes = MAT_BYTES;
    uint64_t app_bytes;
    app_bytes = 3 * MAT_BYTES;

    uint64_t *hMem;
    uint64_t aMem[output_bytes];
    uint64_t bMem[output_bytes];
    uint64_t cMem[output_bytes];
    uint64_t n_pages;

    n_pages = input_bytes / hugePageSize + ((input_bytes % hugePageSize > 0) ? 1 : 0);
    cProcess cproc(0, getpid());

    hMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HOST_2M, (uint32_t)n_pages});
    // bMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_pages});
    // cMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_pages});

    uint64_t fpga_data = 345679821;

    cproc.ioSwitch(IODevs::FPGA_DRAM);

    auto start_time = std::chrono::high_resolution_clock::now();

    cproc.invoke({CoyoteOper::OFFLOAD, (void *)hMem, input_bytes, true, true, 0, false});
    cproc.invoke({CoyoteOper::READ, (void *)hMem, input_bytes, true, true, 0, false});
    cproc.invoke({CoyoteOper::WRITE, (void *)hMem, input_bytes, true, true, 0, false});
    cproc.invoke({CoyoteOper::SYNC, (void *)hMem, input_bytes, true, true, 0, false});


    for(int i = 0; i < output_bytes / 8; i++) {
        ((uint64_t*)aMem)[i] = hMem[i];
        ((uint64_t*)bMem)[i] = hMem[i + output_bytes];
    }

    matrixMultiplication(aMem, bMem, cMem, nrows);

    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

    // app_bytes = ddefSize * 4;
    std::cout << "app bytes: " << app_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;
    std::cout << "finished running: " << std::endl;
    std::cout << "time " << time << "us" << std::endl;
    // 1 / 1024 / 1024 / (10^-6) = 0.9536
    std::cout << "throughput " << app_bytes * 0.9536 / time << " MB/s" << std::endl;
}
