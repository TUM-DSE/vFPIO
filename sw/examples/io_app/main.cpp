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


constexpr auto const keyLow = 0xabf7158809cf4f3c;
constexpr auto const keyHigh = 0x2b7e151628aed2a6;

void prepare_sha256(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    auto const plainLow = 0xe93d7e117393172a;
    auto const plainHigh = 0x6bc1bee22e409f96;
    auto const cipherLow = 0xa89ecaf32466ef97;
    auto const cipherHigh = 0x3ad77bb40d7a3660;
    // bytes = 512;

    for (int i = 0; i < bytes / 8; i++)
    {
        ((uint64_t *)mem)[i] = i % 2 ? plainHigh : plainLow;
    }
    
    // {OpID, input_addr, output_addr, input_len, output_len, clr_stat, poll}
    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, bytes, bytes, true, true, 0, false};

    input_bytes = bytes;
    output_bytes = bytes;
    // app_bytes  = 2 * bytes;
}

void check_sha256(void *mem, int bytes)
{
    printf("Check sha256: \n");
    // bool k = true;
    // for(int i = 0; i < bytes / 8; i++) {
    //     if(i%2 ? ((uint64_t*) mem)[i] != cipherHigh : ((uint64_t*) mem)[i] != cipherLow) {
    //         k = false;
    //         break;
    //     }
    // }
}


void prepare_md5(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    auto const plainLow = 0xe93d7e117393172a;
    auto const plainHigh = 0x6bc1bee22e409f96;
    // bytes = 512;

    for (int i = 0; i < bytes / 8; i++)
    {
        ((uint64_t *)mem)[i] = i % 2 ? plainHigh : plainLow;
    }
    
    // {OpID, input_addr, output_addr, input_len, output_len, clr_stat, poll}
    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, bytes, bytes, true, true, 0, false};

    input_bytes = bytes;
    output_bytes = bytes;
    // app_bytes  = 2 * bytes;
}

void check_md5(void *mem, int bytes)
{
    printf("Check md5: \n");
    // bool k = true;
    // for(int i = 0; i < bytes / 8; i++) {
    //     if(i%2 ? ((uint64_t*) mem)[i] != cipherHigh : ((uint64_t*) mem)[i] != cipherLow) {
    //         k = false;
    //         break;
    //     }
    // }
}

void prepare_aes(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    auto const plainLow = 0xe93d7e117393172a;
    auto const plainHigh = 0x6bc1bee22e409f96;
    // bytes = 512;

    for (int i = 0; i < bytes / 8; i++)
    {
        ((uint64_t *)mem)[i] = i % 2 ? plainHigh : plainLow;
    }
    
    // {OpID, input_addr, output_addr, input_len, output_len, clr_stat, poll}
    // invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, bytes, bytes};

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, bytes, bytes, true, true, 0, false};
    // {OpID, input_addr, len, clr_stat, poll, dest, stream} 
    // cs_invoke = {CoyoteOper::TRANSFER, (void *)mem, size, true, true, 0, false};

    input_bytes = bytes;
    output_bytes = bytes;
    // app_bytes  = 2 * bytes;
}

void check_aes(void *mem, int bytes)
{
    auto const cipherLow = 0xa89ecaf32466ef97;
    auto const cipherHigh = 0x3ad77bb40d7a3660;

    printf("Check aes: \n");
    bool k = true;
    for(int i = 0; i < bytes / 8; i++) {
        if(i%2 ? ((uint64_t*) mem)[i] != cipherHigh : ((uint64_t*) mem)[i] != cipherLow) {
            k = false;
            break;
        }
    }
}

void prepare_rng(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const uint64_t size_shift_in = 11;
    const uint64_t linear_in = 0;
    const uint64_t read_in = 0;

    ((uint64_t*)mem)[0] = size_shift_in;
    ((uint64_t*)mem)[1] = linear_in;
    ((uint64_t*)mem)[2] = read_in;
    
    // {OpID, input_addr, output_addr, input_len, output_len, clr_stat, poll}
    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, 64, 64 * (1 << (size_shift_in - 6)) - 1};
    // serverless_map_memory(mem, bytes, (s0_words+s1_words+1)*64, sc_words*64);
    // serverless_load_bitstream(7);

    input_bytes = 64;
    output_bytes = 64 * (1 << (size_shift_in - 6)) - 1;
    // app_bytes  = 2 * bytes;
    // app_bytes  = 64 + 64 * (1 << (size_shift_in - 6)) - 1;
    // app_bytes  = 64 * (1 << size_shift_in) * (1 << 19);
}


void check_rng(void *mem, int bytes)
{
    printf("Check rng: skipping\n");
    // for(int j=0; j<2; j++) {
    // for(int i=0; i<64; i++) {
    //     printf("%02x ", ((unsigned char*)mem)[j*64+i]);
    //     }
    //     printf("\n");
    // }
    // printf("\n");
}


void prepare_gzip(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    for(int i=0; i<bytes; i++) {
        char c = '0'+(i%('z'-'0'));
        ((char*)mem)[i] = c;
    }

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, 512, 128};
    // serverless_map_memory(mem, 2048, 512, 128);
    // serverless_load_bitstream(6);
    input_bytes = 512;
    output_bytes = 128;
    // app_bytes = 512  + 128;
}


void check_gzip(void *mem, int bytes)
{
    printf("Check Gzip: \n");
    for(int j=0; j<2; j++) {
    for(int i=0; i<64; i++) {
        printf("%02x ", ((unsigned char*)mem)[j*64+i]);
        }
        printf("\n");
    }
    printf("\n");
}

void prepare_sha256hls(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    for(int i=0; i<bytes; i++) {
        ((char*)mem)[i] = 'f';
    }
    //((char*)mem)[0] = 'b';
    //((char*)mem)[66] = 'c';

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, 64, 32};
    // serverless_map_memory(mem, bytes, 64, 32);
    // serverless_load_bitstream(8);
    input_bytes = 64;
    output_bytes = 32;
    // app_bytes = 64 + 32;
}

void check_sha256hls(void *mem, int bytes)
{
    printf("Check SHA-256 hls: ");
    for(int i=0; i<32; i++) {
        printf("%02x", ((uint8_t*)mem)[i]);
    }
    printf("\n");
    for(int i=0; i<32; i++) {
        uint8_t b = ((uint8_t*)mem)[i];
        b = (b * 0x0202020202ULL & 0x010884422010ULL) % 1023;
        printf("%02x", b);
    }
    printf("\n");
}

void prepare_hls4ml(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    FILE * fd;
    fd = fopen("tb_input_features.dat","r");
    if(fd==NULL) {
        perror("could not open file");
        exit(1);
    }

    short *smem = (short*)mem;
    float fpv;
    
    for(int i=0; fscanf(fd, "%f", &fpv)>0; i++) {
        assert(i*2 <= bytes);

        short fixp = fpv*(1<<10) + 0.5;
        smem[i] = fixp;
        hls4ml_samples = (i+1)/32/32/3;
    }
    fclose(fd);

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, hls4ml_samples*32*32*3*2, hls4ml_samples*64};
    // serverless_map_memory(mem, bytes, hls4ml_samples*32*32*3*2, hls4ml_samples*64);
    // serverless_load_bitstream(9);
    input_bytes = hls4ml_samples*32*32*3*2;
    output_bytes = hls4ml_samples*64;
    // app_bytes = hls4ml_samples*32*32*3*2 + hls4ml_samples*64;
}

void check_hls4ml(void *mem, int bytes)
{
    printf("Check hls4ml: ");
    short *smem = (short*)mem;
    for(int i=0; i<hls4ml_samples; i++) {
        int maxarg=-1;
        float maxval=-1;
        for(int j=0; j<10; j++) {
            short fixp = smem[i*32+j];
            float fpv = ((float)fixp)/(1<<10);
            printf("%.4f ", fpv);
            if(fpv > maxval) {
                maxarg = j;
                maxval = fpv;
            }
        }
        printf(" -->  %d \n", maxarg);
    }
}

void prepare_sha3(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    for(int i=0; i<bytes; i++) {
        ((char*)mem)[i] = 'a';
    }
    ((char*)mem)[0] = 'b';
    ((char*)mem)[66] = 'c';

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, 128, 64};
    // serverless_map_memory(mem, bytes, 128, 64);
    // serverless_load_bitstream(0);
    input_bytes = 128;
    output_bytes = 64;
    // app_bytes = 128 + 64;
}


void check_sha3(void *mem, int bytes)
{
    printf("Check SHA3: ");
    for(int i=0; i<8; i++) {
        printf("%lx", ((uint64_t*)mem)[7-i]);
    }
    printf("\n");
}


void prepare_matmul(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const int MAT_BYTES = 64*64*8;
    assert(bytes >= 2*MAT_BYTES);
    
    for(int i=0; i<bytes/8; i++) {
	    ((uint64_t*)mem)[i] = -2345+i;
    }

    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, 2 * MAT_BYTES, MAT_BYTES};
    // serverless_map_memory(mem, bytes, 2*MAT_BYTES, MAT_BYTES);
    // serverless_load_bitstream(5);
    input_bytes = 2 * MAT_BYTES;
    output_bytes = MAT_BYTES;
    // app_bytes = 3 * MAT_BYTES;
}

void check_matmul(void *mem, int bytes)
{
    printf("Check MatMul: \n");
    // for(int r=0; r<64*64/8; r++) {
    //     for(int i=0; i<8; i++) {
    //         printf("%ld ", ((uint64_t*)mem)[r*8+i]);
    //     }
    //     printf("\n");
    // }
    printf("\n");
}


void prepare_nw(void *mem, int bytes, csInvokeAll &invoke_op, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const uint64_t s_ratio = 512/128;
    const uint64_t sc_ratio = 512/8;
    const uint64_t s0_words = 32;
    const uint64_t s1_words = 32;
    const uint64_t sc_count = s0_words * s_ratio * s1_words * s_ratio;
    const uint64_t sc_words = (sc_count+sc_ratio-1) / sc_ratio;


    std::cout << "sc_count: " << sc_count << std::endl;
    std::cout << "sc_words: " << sc_words << std::endl;
    
    assert((s0_words+s1_words+1)*64 < bytes);
    assert(sc_words*64 < bytes);
    
    ((uint64_t*)mem)[0] = s0_words;
    ((uint64_t*)mem)[1] = s1_words;
    ((uint64_t*)mem)[2] = sc_count;
    ((uint64_t*)mem)[3] = sc_words;
    
    for(uint32_t i=0; i<s0_words+s1_words; i++)
        for(uint32_t j=0; j<64; j++)
            ((uint8_t*)mem)[(i+1)*64+j] = (i*31+j*37)%251;

    // {OpID, input_addr, output_addr, input_len, output_len, clr_stat, poll}
    // invoke_op = {CoyoteOper::WRITE, (void *)mem, (void *)mem, (s0_words+s1_words+1)*64, sc_words*64};
    invoke_op = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, (s0_words+s1_words+1)*64, sc_words*64, true, true, 0, false};

    // serverless_map_memory(mem, bytes, (s0_words+s1_words+1)*64, sc_words*64);
    // serverless_load_bitstream(7);
    input_bytes = (s0_words+s1_words+1)*64;
    output_bytes = sc_words*64;
    // app_bytes = (s0_words + s0_words * s1_words * s_ratio + sc_words) * 64;
}

void check_nw(void *mem, int bytes)
{
    printf("Check NW: \n");
    for(int j=0; j<2; j++) {
    for(int i=0; i<64; i++) {
        printf("%02x ", ((uint8_t*)mem)[j*64+i]);
        }
        printf("\n");
    }
    printf("\n");
    
}


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

    if (opId == "") {
        std::cout << "opeartor is: null" << std::endl;
        return 1;
    }
    std::cout << "opeartor is: " << opId << std::endl;
    std::cout << "huge: " << huge << std::endl;
    std::cout << "vio: " << vio << std::endl;
    std::cout << "fpga_mem: " << fpga_mem << std::endl;

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
    if (vio) {
        cproc.ioSwDbg();
        if (fpga_mem) {
            io_dev = IODevs::FPGA_DRAM;
            io_target = 0x02;
        } else {
            io_dev = IODevs::HOST_MEM;
            io_target = 0x01;
        }

        auto io_start_time = std::chrono::high_resolution_clock::now();
        // io_dev = ioDev;
        cproc.ioSwitch(io_dev);
        // cproc.ioSwDbg();

        while (io_status != io_target){
            io_status = cproc.ioStatus();
            // std::cout << io_status << std::endl;
        }
        auto io_end_time = std::chrono::high_resolution_clock::now();
        double io_time = std::chrono::duration_cast<std::chrono::microseconds>(io_end_time - io_start_time).count();
        std::cout << "io time " << io_time << "us" << std::endl;

    }

    csInvokeAll invoke_op;

    if(opId == "nw") prepare_nw(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "mat") prepare_matmul(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "sha3") prepare_sha3(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "sha256hls") prepare_sha256hls(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "gzip") prepare_gzip(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "hls4ml") prepare_hls4ml(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "rng") prepare_rng(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "aes") {
        prepare_aes(mem, size, invoke_op, input_bytes, output_bytes);
        cproc.setCSR(keyLow, 0);
        cproc.setCSR(keyHigh, 1);
    }
    if(opId == "md5") {
        prepare_md5(mem, size, invoke_op, input_bytes, output_bytes);
        // cproc.setCSR(keyLow, 0);
        // cproc.setCSR(keyHigh, 1);
    }
    if(opId == "sha256") {
        prepare_sha256(mem, size, invoke_op, input_bytes, output_bytes);
        // cproc.setCSR(keyLow, 0);
        // cproc.setCSR(keyHigh, 1);
    }
    app_bytes = input_bytes + output_bytes;
    std::cout << "input bytes: " << input_bytes << " B" << std::endl;
    std::cout << "output bytes: " << output_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes << " B" << std::endl;
    std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;

    // return 0;
    // std::cout << "oper after assign: " << static_cast<std::underlying_type<CoyoteOper>::type>(invoke_op.oper) << std::endl;
    // csInvoke cs_invoke;

    // cs_invoke = {CoyoteOper::TRANSFER, (void *)mem, (void *)mem, bytes, bytes};
    // cs_invoke = {CoyoteOper::TRANSFER, (void *)mem, size, true, true, 0, false};

    auto start_time = std::chrono::high_resolution_clock::now();

    if (io_dev == IODevs::HOST_MEM && !fpga_mem) {
        std::cout << "Using host mem." << std::endl;
        invoke_op.oper = CoyoteOper::TRANSFER;
        invoke_op.stream = true;
        cproc.invoke(invoke_op);
    }
    else {
        std::cout << "Using fpga mem." << std::endl;
        invoke_op.oper = CoyoteOper::OFFLOAD;
        
        invoke_op.stream = false;
        // cproc.invoke(invoke_op);
        cproc.invoke({CoyoteOper::OFFLOAD, (void *)mem, input_bytes, true, true, 0, false});

        invoke_op.oper = CoyoteOper::READ;
        // cproc.invoke(invoke_op);
        cproc.invoke({CoyoteOper::READ, (void *)mem, input_bytes, true, true, 0, false});

        invoke_op.oper = CoyoteOper::WRITE;
        // cproc.invoke(invoke_op);
        cproc.invoke({CoyoteOper::WRITE, (void *)mem, output_bytes, true, true, 0, false});

        invoke_op.oper = CoyoteOper::SYNC;
        // cproc.invoke(invoke_op);
        cproc.invoke({CoyoteOper::SYNC, (void *)mem, output_bytes, true, true, 0, false});

    }

    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

    std::cout << "finished running: " << std::endl;
    std::cout << "time " << time << "us" << std::endl;
    // 1 / 1024 / 1024 / (10^-6) = 0.9536
    std::cout << "throughput " << app_bytes * 0.9536 / time << " MB/s" << std::endl;

    if(opId == "nw") check_nw(mem, size);
    if(opId == "mat") check_matmul(mem, size);
    if(opId == "sha3") check_sha3(mem, size);
    if(opId == "sha256hls") check_sha256hls(mem, size);
    if(opId == "gzip") check_gzip(mem, size);
    if(opId == "hls4ml") check_hls4ml(mem, size);
    if(opId == "rng") check_rng(mem, size);
    if(opId == "aes") check_aes(mem, size);
    if(opId == "md5") check_md5(mem, size);
    if(opId == "sha256") check_sha256(mem, size);
    

    std::cout << "results: " << std::endl;
    for(int i=0; i<16; i++) {
        uint64_t val = ((uint64_t*)mem)[i];
        printf("%s 0x%lx", (i==0 ? "" : ","), val);
    }
    std::cout << " ..." << std::endl;

    return (EXIT_SUCCESS);
}
