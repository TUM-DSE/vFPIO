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
#include <openssl/evp.h>
#include <openssl/err.h>
#include <openssl/sha.h>

#include "cProcess.hpp"

using namespace fpga;

constexpr auto const ddefSize = 128;

unsigned char *sha3_hash(const unsigned char *data, size_t data_len)
{
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx == NULL)
    {
        return NULL;
    }

    int err = EVP_DigestInit_ex(mdctx, EVP_sha3_256(), NULL);
    if (err != 1)
    {
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    err = EVP_DigestUpdate(mdctx, data, data_len);
    if (err != 1)
    {
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    unsigned char *md = (unsigned char *)malloc(EVP_MAX_MD_SIZE);
    unsigned int md_len;
    err = EVP_DigestFinal_ex(mdctx, md, &md_len);
    if (err != 1)
    {
        free(md);
        EVP_MD_CTX_free(mdctx);
        return NULL;
    }

    EVP_MD_CTX_free(mdctx);

    return md;
}
int main(int argc, char *argv[])
{
    uint32_t d_data_size = ddefSize;
    uint64_t app_bytes;

    uint64_t *aMem;
    uint64_t n_pages;

    n_pages = d_data_size / hugePageSize + ((d_data_size % hugePageSize > 0) ? 1 : 0);
    cProcess cproc(0, getpid());

    aMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HOST_2M, (uint32_t)n_pages});

    uint64_t fpga_data = 345679821;

    cproc.ioSwitch(IODevs::FPGA_DRAM);

    auto start_time = std::chrono::high_resolution_clock::now();


    cproc.invoke({CoyoteOper::OFFLOAD, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::READ, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::WRITE, (void *)aMem, d_data_size, true, true, 0, false});
    cproc.invoke({CoyoteOper::SYNC, (void *)aMem, d_data_size, true, true, 0, false});

    sha3_hash((const unsigned char *)aMem, d_data_size);


    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

    app_bytes = 128 + 64;
    std::cout << "app bytes: " << app_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;
    std::cout << "finished running: " << std::endl;
    std::cout << "time " << time << "us" << std::endl;
    // 1 / 1024 / 1024 / (10^-6) = 0.9536
    std::cout << "throughput " << app_bytes * 0.9536 / time << " MB/s" << std::endl;
}
