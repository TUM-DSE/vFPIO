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
#include "gzip/compress.hpp"
#include <gzip/utils.hpp>
#include <openssl/evp.h>
#include <openssl/aes.h>
#include <openssl/md5.h>

using namespace fpga;

// Default size in bytes
constexpr auto const defSize = 64 * 1024;

// Read size
constexpr auto const rdSize = 4 * 1024;

// Deafult IO device
constexpr auto const ioDev = IODevs::FPGA_DRAM;

// AES data
constexpr auto const keyLow = 0xabf7158809cf4f3c;
constexpr auto const keyHigh = 0x2b7e151628aed2a6;
constexpr auto const plainLow = 0xe93d7e117393172a;
constexpr auto const plainHigh = 0x6bc1bee22e409f96;
constexpr auto const cipherLow = 0xa89ecaf32466ef97;
constexpr auto const cipherHigh = 0x3ad77bb40d7a3660;

const unsigned char aes_key[16] = {0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c, 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6};

unsigned char digest[MD5_DIGEST_LENGTH];

unsigned char *md5(const unsigned char *data, size_t length)
{
    // Check if the data is NULL or has zero length.
    if (data == nullptr || length == 0)
    {
        return nullptr;
    }

    // Create an MD5 context.
    MD5_CTX ctx;
    MD5_Init(&ctx);

    // Update the context with the data.
    MD5_Update(&ctx, data, length);

    // Get the MD5 digest.
    MD5_Final(digest, &ctx);

    // Return the MD5 digest.
    return digest;
}

int encrypt_aes_ecb(const unsigned char *plaintext, int plaintext_len,
                    const unsigned char *key, unsigned char *ciphertext)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL)
    {
        std::cout << "Error: EVP_CIPHER_CTX_new" << std::endl;
        return -1;
    }

    int err = EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, key, NULL);
    if (err != 1)
    {
        EVP_CIPHER_CTX_free(ctx);
        std::cout << "Error: EVP_EncryptInit_ex" << std::endl;
        return err;
    }

    err = EVP_EncryptUpdate(ctx, ciphertext, &plaintext_len, plaintext, plaintext_len);
    if (err != 1)
    {
        std::cout << "Error: EVP_EncryptUpdate" << std::endl;
        EVP_CIPHER_CTX_free(ctx);
        return err;
    }

    err = EVP_EncryptFinal_ex(ctx, ciphertext + plaintext_len, &plaintext_len);
    if (err != 1)
    {
        std::cout << "Error: EVP_EncryptFinal_ex" << std::endl;
        EVP_CIPHER_CTX_free(ctx);
        return err;
    }

    EVP_CIPHER_CTX_free(ctx);

    return plaintext_len;
}

unsigned char *calculate_sha256(const unsigned char *data, size_t data_len)
{
    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (mdctx == NULL)
    {
        return NULL;
    }

    int err = EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL);
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
    std::string opId;

    boost::program_options::options_description programDescription("Options:");
    programDescription.add_options()
        ("operator,o", boost::program_options::value<std::string>(&opId), "Operator")
        ("benchmark,b", boost::program_options::value<uint32_t>(), "Benchmark application");

    boost::program_options::variables_map commandLineArgs;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, programDescription), commandLineArgs);
    boost::program_options::notify(commandLineArgs);

    /*
     * 0: AES-ECB Encrypt
     * 1: SHA256
     * 2: GZIP compress
     * 3: MD5
     */
    uint32_t bench_op;
    if (commandLineArgs.count("benchmark") > 0)
        bench_op = commandLineArgs["benchmark"].as<uint32_t>();
    else
        bench_op = 0;

    if (opId == "") {
        std::cout << "opeartor is: null" << std::endl;
        return 1;
    }
    std::cout << "opeartor is: " << opId << std::endl;

    uint32_t size = defSize;
    IODevs io_dev = ioDev;
    uint64_t n_pages;
    uint64_t app_bytes;

    cProcess cproc(0, getpid());

    n_pages = size / hugePageSize + ((size % hugePageSize > 0) ? 1 : 0);

    // Allocate test data and result data
    void *fMem = (uint64_t *)cproc.getMem({CoyoteAlloc::HUGE_2M, (uint32_t)n_pages});

    for (int i = 0; i < size / 8; i++)
    {
        ((uint64_t *)fMem)[i] = i % 2 ? (plainHigh ^ 0xFFFFFFFFFFFFFFFF) : (plainLow ^ 0xFFFFFFFFFFFFFFFF);
    }

    // IO device: use fpga dram
    cproc.ioSwitch(io_dev);

    // Write data to FPGA DRAM
    cproc.invoke({CoyoteOper::OFFLOAD, (void *)fMem, size, true, true, 0, false});

    // Use dummy hardware to flip bits
    cproc.invoke({CoyoteOper::READ, (void *)fMem, size, true, true, 0, false});
    cproc.invoke({CoyoteOper::WRITE, (void *)fMem, size, true, true, 0, false});

    auto start_time = std::chrono::high_resolution_clock::now();

    // Read back actual data from FPGA memory
    for (int i = 0; i < size / rdSize; i++)
    {
        cproc.invoke({CoyoteOper::SYNC, (void *)((uint64_t *)fMem + (i * (rdSize / 8))), rdSize, true, true, 0, false});

        // Check data
        bool k = true;
        std::cout << i + 1 << " blocks have been read" << std::endl;
        for (int j = 0; j < size / 8; j++)
        {
            if (j % 2 ? ((uint64_t *)fMem)[j] != plainHigh : ((uint64_t *)fMem)[j] != plainLow)
            {
                std::cout << j + 1 << " block has failure" << std::endl;
                k = false;
                break;
            }
        }

        std::cout << (k ? "Success: Data has been flipped!" : "Error: Data flipping failed") << std::endl;
    }


    // Call the required operation
    if(opId == "aes") {
        // AES
        // TODO: Check cipher data
        unsigned char *cipherData = (unsigned char *)cproc.getMem({CoyoteAlloc::HOST_2M, (uint32_t)n_pages});
        encrypt_aes_ecb((const unsigned char *)fMem, size, aes_key, cipherData);
    }
    if(opId == "md5") {
        // md5
        std::cout << "md5" << std::endl;
        md5((const unsigned char *)fMem, size);
    }
    if(opId == "sha256") {
        // SHA256
        std::cout << "SHA256" << std::endl;
        calculate_sha256((const unsigned char *)fMem, size);
    }

    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

    app_bytes = size;
    std::cout << "app bytes: " << app_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;
    std::cout << "time " << time << "us" << std::endl;
    std::cout << "throughput " << app_bytes * 0.9536 / time << " MB/s" << std::endl;
}