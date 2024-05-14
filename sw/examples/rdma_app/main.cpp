#include "cDefs.hpp"

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
#include <random>
#include <cstring>
#include <atomic>
#include <signal.h> 
#include <boost/program_options.hpp>
#include <fmt/printf.h>
#include <openssl/evp.h>
#include <openssl/aes.h>
#include <openssl/md5.h>

#include "cBench.hpp"
#include "ibvQpMap.hpp"

#define EN_THR_TESTS
// #define EN_LAT_TESTS

using namespace std;
using namespace std::chrono;
using namespace fpga;

/* Signal handler */
std::atomic<bool> stalled(false); 
void gotInt(int) {
    stalled.store(true);
}

/* Params */
constexpr auto const targetRegion = 0;
constexpr auto const qpId = 0;
constexpr auto const port = 18488;

/* Bench */
constexpr auto const defNBenchRuns = 1; 
constexpr auto const defNRepsThr = 1;
constexpr auto const defNRepsLat = 1;
constexpr auto const defMinSize = 65536;
constexpr auto const defMaxSize = 65536;
constexpr auto const defOper = 0;
constexpr auto const plainLow = 0xe93d7e117393172a;
constexpr auto const plainHigh = 0x6bc1bee22e409f96;
const unsigned char aes_key[16] = {0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c, 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6};
constexpr auto const defvIO = false;

void prepare_nw(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const uint64_t s_ratio = 512/128;
    const uint64_t sc_ratio = 512/8;
    const uint64_t s0_words = 32;
    const uint64_t s1_words = 32;
    const uint64_t sc_count = s0_words * s_ratio * s1_words * s_ratio;
    const uint64_t sc_words = (sc_count+sc_ratio-1) / sc_ratio;
    
    assert((s0_words+s1_words+1)*64 < bytes);
    assert(sc_words*64 < bytes);
    
    ((uint64_t*)mem)[0] = s0_words;
    ((uint64_t*)mem)[1] = s1_words;
    ((uint64_t*)mem)[2] = sc_count;
    ((uint64_t*)mem)[3] = sc_words;
    
    for(uint32_t i=0; i<s0_words+s1_words; i++)
        for(uint32_t j=0; j<64; j++)
            ((uint8_t*)mem)[(i+1)*64+j] = (i*31+j*37)%251;

    input_bytes = (s0_words+s1_words+1)*64;
    output_bytes = sc_words*64;
    // app_bytes = (s0_words + s0_words * s1_words * s_ratio + sc_words) * 64;
}

void prepare_matmul(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const int MAT_BYTES = 64*64*8;
    assert(bytes >= 2*MAT_BYTES);
    
    for(int i=0; i<bytes/8; i++) {
	    ((uint64_t*)mem)[i] = -2345+i;
    }

    input_bytes = 2 * MAT_BYTES;
    output_bytes = MAT_BYTES;
    // app_bytes = 3 * MAT_BYTES;
}

void prepare_sha3(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    for(int i=0; i<bytes; i++) {
        ((char*)mem)[i] = 'a';
    }
    ((char*)mem)[0] = 'b';
    ((char*)mem)[66] = 'c';

    input_bytes = 128;
    output_bytes = 64;
    // app_bytes = 128 + 64;
}

void prepare_rng(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    const uint64_t size_shift_in = 11;
    const uint64_t linear_in = 0;
    const uint64_t read_in = 0;

    ((uint64_t*)mem)[0] = size_shift_in;
    ((uint64_t*)mem)[1] = linear_in;
    ((uint64_t*)mem)[2] = read_in;

    input_bytes = 64;
    output_bytes = 64 * (1 << (size_shift_in - 6)) - 1;
    // app_bytes  = 2 * bytes;
    // app_bytes  = 64 + 64 * (1 << (size_shift_in - 6)) - 1;
    // app_bytes  = 64 * (1 << size_shift_in) * (1 << 19);
}

void prepare_hls4ml(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    FILE * fd;
    fd = fopen("tb_input_features.dat","r");
    if(fd==NULL) {
        perror("could not open file");
        exit(1);
    }
    
    int hls4ml_samples = 0;
    short *smem = (short*)mem;
    float fpv;
    
    for(int i=0; fscanf(fd, "%f", &fpv)>0; i++) {
        assert(i*2 <= bytes);

        short fixp = fpv*(1<<10) + 0.5;
        smem[i] = fixp;
        hls4ml_samples = (i+1)/32/32/3;
    }
    fclose(fd);

    input_bytes = hls4ml_samples*32*32*3*2;
    output_bytes = hls4ml_samples*64;
    // app_bytes = hls4ml_samples*32*32*3*2 + hls4ml_samples*64;
}

void prepare_gzip(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    for(int i=0; i<bytes; i++) {
        char c = '0'+(i%('z'-'0'));
        ((char*)mem)[i] = c;
    }

    input_bytes = 512;
    output_bytes = 128;
    // app_bytes = 512  + 128;
}

void prepare_aes(void *mem, int bytes, uint64_t &input_bytes, uint64_t &output_bytes)
{
    auto const plainLow = 0xe93d7e117393172a;
    auto const plainHigh = 0x6bc1bee22e409f96;
    // bytes = 64 * 1024;

    for (int i = 0; i < bytes / 8; i++)
    {
        ((uint64_t *)mem)[i] = i % 2 ? plainHigh : plainLow;
    }

    input_bytes = bytes;
    output_bytes = bytes;
    // app_bytes  = 2 * bytes;
}

int main(int argc, char *argv[])  
{
    // ---------------------------------------------------------------
    // Initialization 
    // ---------------------------------------------------------------

    // Sig handler
    struct sigaction sa;
    memset( &sa, 0, sizeof(sa) );
    sa.sa_handler = gotInt;
    sigfillset(&sa.sa_mask);
    sigaction(SIGINT,&sa,NULL);
    bool vio = defvIO;
    std::string opId;

    // Read arguments
    boost::program_options::options_description programDescription("Options:");
    programDescription.add_options()
        ("tcpaddr,t", boost::program_options::value<string>(), "TCP conn IP")
        ("benchruns,b", boost::program_options::value<uint32_t>(), "Number of bench runs")
        ("repst,r", boost::program_options::value<uint32_t>(), "Number of throughput repetitions within a run")
        ("repsl,l", boost::program_options::value<uint32_t>(), "Number of latency repetitions within a run")
        ("mins,n", boost::program_options::value<uint32_t>(), "Minimum transfer size")
        ("maxs,x", boost::program_options::value<uint32_t>(), "Maximum transfer size")
        ("operator,o", boost::program_options::value<std::string>(&opId), "Operator")
        ("vio,i", boost::program_options::bool_switch(&vio), "vIO")
        ("oper,w", boost::program_options::value<bool>(), "Read or Write");
    
    boost::program_options::variables_map commandLineArgs;
    boost::program_options::store(boost::program_options::parse_command_line(argc, argv, programDescription), commandLineArgs);
    boost::program_options::notify(commandLineArgs);

    // Stat
    string tcp_mstr_ip;
    uint32_t n_bench_runs = defNBenchRuns;
    uint32_t n_reps_thr = defNRepsThr;
    uint32_t n_reps_lat = defNRepsLat;
    uint32_t min_size = defMinSize;
    uint32_t max_size = defMaxSize;
    bool oper = defOper;
    bool mstr = true;

    char const* env_var_ip = std::getenv("FPGA_0_IP_ADDRESS");
    if(env_var_ip == nullptr) 
        throw std::runtime_error("IBV IP address not provided");
    string ibv_ip(env_var_ip);

    if(commandLineArgs.count("tcpaddr") > 0) {
        tcp_mstr_ip = commandLineArgs["tcpaddr"].as<string>();
        mstr = false;
    }
        
    if (opId == "") {
        std::cout << "opeartor is: null" << std::endl;
        return 1;
    }
    std::cout << "opeartor is: " << opId << std::endl;

    if(commandLineArgs.count("benchruns") > 0) n_bench_runs = commandLineArgs["benchruns"].as<uint32_t>();
    if(commandLineArgs.count("repst") > 0) n_reps_thr = commandLineArgs["repst"].as<uint32_t>();
    if(commandLineArgs.count("repsl") > 0) n_reps_lat = commandLineArgs["repsl"].as<uint32_t>();
    if(commandLineArgs.count("mins") > 0) min_size = commandLineArgs["mins"].as<uint32_t>();
    if(commandLineArgs.count("maxs") > 0) max_size = commandLineArgs["maxs"].as<uint32_t>();
    if(commandLineArgs.count("oper") > 0) oper = commandLineArgs["oper"].as<bool>();

    uint32_t n_pages = (max_size + hugePageSize - 1) / hugePageSize;
    uint32_t size = min_size;
    uint64_t input_bytes;
    uint64_t output_bytes;
    uint64_t app_bytes;

    PR_HEADER("PARAMS");
    if(!mstr) { std::cout << "TCP master IP address: " << tcp_mstr_ip << std::endl; }
    std::cout << "IBV IP address: " << ibv_ip << std::endl;
    std::cout << "Number of allocated pages: " << n_pages << std::endl;
    std::cout << (oper ? "Write operation" : "Read operation") << std::endl;
    std::cout << "Min size: " << min_size << std::endl;
    std::cout << "Max size: " << max_size << std::endl;
    std::cout << "Number of throughput reps: " << n_reps_thr << std::endl;
    std::cout << "Number of latency repsss: " << n_reps_lat << std::endl;
    std::cout << "vio: " << vio << std::endl;

    // Create  queue pairs
    ibvQpMap ictx;
    ictx.addQpair(qpId, targetRegion, ibv_ip, n_pages);
    mstr ? ictx.exchangeQpMaster(port) : ictx.exchangeQpSlave(tcp_mstr_ip.c_str(), port);
    ibvQpConn *iqp = ictx.getQpairConn(qpId);
    cProcess *cproc = iqp->getCProc();

    // Init app layer --------------------------------------------------------------------------------

    uint64_t *hMem = (uint64_t*)iqp->getQpairStruct()->local.vaddr;

    if (vio) {
        cproc->ioSwitch(IODevs::RDMA_0_HOST_SEND);
    }

    iqp->ibvSync(mstr);

    if(opId == "nw") prepare_nw(hMem, size, input_bytes, output_bytes);
    if(opId == "mat") prepare_matmul(hMem, size, input_bytes, output_bytes);
    if(opId == "sha3") prepare_sha3(hMem, size, input_bytes, output_bytes);
    // if(opId == "sha256hls") prepare_sha256hls(mem, size, invoke_op, input_bytes, output_bytes);
    if(opId == "gzip") prepare_gzip(hMem, size, input_bytes, output_bytes);
    if(opId == "rng") prepare_rng(hMem, size, input_bytes, output_bytes);
    if(opId == "hls4ml") prepare_hls4ml(hMem, size, input_bytes, output_bytes);
    if(opId == "aes") prepare_aes(hMem, size, input_bytes, output_bytes);
    if(opId == "md5") prepare_aes(hMem, size, input_bytes, output_bytes);
    if(opId == "sha256") prepare_aes(hMem, size, input_bytes, output_bytes);
    if(opId == "perf") {
        uint64_t fill = (mstr) ? 3 : 9;
        // Fill the data
        for(int i = 0; i < max_size/64; i++) {
            for(int j = 0; j < 8; j++) {
                hMem[i*8+j] = fill;
            } 
        } 
    }

    app_bytes = input_bytes + output_bytes;


    struct ibvSge sg;
    struct ibvSendWr wr;
    
    memset(&sg, 0, sizeof(sg));
    sg.type.rdma.local_offs = 0;
    sg.type.rdma.remote_offs = 0;
    sg.type.rdma.len = input_bytes;
    std::cout << "len: " << sg.type.rdma.len << std::endl;
    std::cout << "app_bytes: " << app_bytes << std::endl;


    memset(&wr, 0, sizeof(wr));
    wr.sg_list = &sg;
    wr.num_sge = 1;
    wr.opcode = oper ? IBV_WR_RDMA_WRITE : IBV_WR_RDMA_READ;

    PR_HEADER("RDMA BENCHMARK");
    // Setup
    iqp->ibvClear();
    iqp->ibvSync(mstr);
    // while(sg.type.rdma.len <= max_size) {

        // Measurements ----------------------------------------------------------------------------------
        if(mstr) {
            // Inititator 
	    //
	    //cproc->netDrop(1, 0, 0);
	    //cproc->netDrop(0, 1, 0);
            
            // ---------------------------------------------------------------
            // Runs 
            // ---------------------------------------------------------------
            cBench bench(n_bench_runs);
            uint32_t n_runs = 0;

#ifdef EN_THR_TESTS    
            auto benchmark_thr = [&]() {
                bool k = false;
                n_runs++;
                
                // Initiate
                for(int i = 0; i < n_reps_thr; i++) {
                    iqp->ibvPostSend(&wr);
                }

                // Wait for completion
                while(iqp->ibvDone() < n_reps_thr * n_runs) { 
                    if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  
                    // std::cout << iqp->ibvDone() << std::endl;
                }
            };
            std::cout << "in master" << std::endl;
            bench.runtime(benchmark_thr);
            std::cout << std::fixed << std::setprecision(2);
            std::cout << std::setw(8) << app_bytes << " [bytes], throughput: " 
                      << std::setw(8) << ((1 + oper) * ((1000 * app_bytes))) / ((bench.getAvg()) / n_reps_thr) << " [MB/s], latency: "
                      << ((bench.getAvg()) / n_reps_thr / 1000) << "us"; 

            std::cout << std::endl << std::endl << "ACKs: " << cproc->ibvCheckAcks() << std::endl;
#endif
            
            // Reset
            // iqp->ibvClear();
            // n_runs = 0;
            // //std::cout << "\e[1mSyncing ...\e[0m" << std::endl;
            // iqp->ibvSync(mstr);

#ifdef EN_LAT_TESTS           
            auto benchmark_lat = [&]() {
                n_runs++;
                
                // Initiate and wait for completion
                for(int i = 0; i < n_reps_lat; i++) {
                    // std::cout << "n_reps_lat: " << i << std::endl;
                    iqp->ibvPostSend(&wr);
                    while(iqp->ibvDone() < (i+1) + ((n_runs-1) * n_reps_lat)) { if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  }
                }
            };
            bench.runtime(benchmark_lat);
	    std::cout << (bench.getAvg()) / (n_reps_lat * (1 + oper)) << " [ns]" << std::endl;
#endif	    

        } else {
            // Server

            if(oper) {
                auto start_time = std::chrono::high_resolution_clock::now();
#ifdef EN_THR_TESTS
                for(uint32_t n_runs = 1; n_runs <= n_bench_runs; n_runs++) {
                    bool k = false;
                    
                    // Wait for incoming transactions
                    while(iqp->ibvDone() < n_reps_thr * n_runs) { 
                        if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  
                    }
                    // std::cout << "iqp->ibvDone()" << std::endl;
                    // Send back
                    for(int i = 0; i < n_reps_thr + 5; i++) {
                        iqp->ibvPostSend(&wr);
                    }
                }
#endif

                // // Reset
                // iqp->ibvClear();
                // //std::cout << "\e[1mSyncing ...\e[0m" << std::endl;
                // iqp->ibvSync(mstr);

#ifdef EN_LAT_TESTS
                for(int n_runs = 1; n_runs <= n_bench_runs; n_runs++) {
                    
                    // Wait for the incoming transaction and send back
                    for(int i = 0; i < n_reps_lat; i++) {
                    //   std::cout << "n_reps_lat: " << i << std::endl;
                        while(iqp->ibvDone() < (i+1) + ((n_runs-1) * n_reps_lat)) { if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  }
                        iqp->ibvPostSend(&wr);
                    }
                } 
#endif		
                auto end_time = std::chrono::high_resolution_clock::now();
                double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
                // double time_2 = std::chrono::duration_cast<std::chrono::microseconds>(end_time_2 - start_time).count();
                std::cout << "app bytes: " << app_bytes << " B" << std::endl;
                std::cout << "app bytes: " << app_bytes / 1024  << " KB" << std::endl;
                std::cout << "time " << time << "us" << std::endl;
                // std::cout << "trans time " << time_2 << "us" << std::endl;
                std::cout << "throughput " << app_bytes * 0.9536 / time * n_reps_thr << " MB/s" << std::endl;
            } else {
                std::cout << "\e[1mSyncing ...\e[0m" << std::endl;
                iqp->ibvSync(mstr);
            }
        }  

    //     sg.type.rdma.len *= 2;
    // }
    std::cout << std::endl;

    
    fmt::print("\n[{}] before cleanup let's print our local memory \n", __func__);
    std::this_thread::sleep_for(500ms);
    // for (auto idx = 0; idx < max_size; idx++) {
    //     fmt::print("{}", hMem[idx]);
    //     if ((idx + 1) % size == 0)
    //     std::cout << "\n";
    // }

    // for(int i = 0; i < max_size/64; i++) {
    //     for(int j = 0; j < 8; j++) {
    //         fmt::print("{} ", hMem[i*8+j]);
    //     } 
    //     std::cout << "\n";
    // } 
    // fmt::print("\n");

    // Done
    if (mstr) {
        iqp->sendAck(1);
        iqp->closeAck();
    } else {
        iqp->readAck();
        iqp->closeConnection();
    }


    // fmt::print("aes finished\n");
    return EXIT_SUCCESS;
}