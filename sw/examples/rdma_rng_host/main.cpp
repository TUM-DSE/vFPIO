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
#include <gzip/utils.hpp>
#include "gzip/compress.hpp"


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
constexpr auto const defNRepsThr = 65536;
constexpr auto const defNRepsLat = 1;
constexpr auto const defMinSize = 65536;
constexpr auto const defMaxSize = 65536;
constexpr auto const defOper = 0;
constexpr auto const plainLow = 0xe93d7e117393172a;
constexpr auto const plainHigh = 0x6bc1bee22e409f96;
const unsigned char aes_key[16] = {0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c, 0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6};
unsigned char digest[MD5_DIGEST_LENGTH];

constexpr auto const defvIO = false;

constexpr auto const bram_size = 1024;
constexpr auto const ddefSize = 64;

uint32_t permute(uint32_t idx)
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
        ("benchmark,m", boost::program_options::value<uint32_t>(), "Benchmark application")
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

    /*
     * 0: AES-ECB Encrypt
     * 1: SHA256
     * 2: MD5
     */
    uint32_t bench_op;
    if (commandLineArgs.count("benchmark") > 0)
        bench_op = commandLineArgs["benchmark"].as<uint32_t>();
    else
        bench_op = 0;
        
    if(commandLineArgs.count("benchruns") > 0) n_bench_runs = commandLineArgs["benchruns"].as<uint32_t>();
    if(commandLineArgs.count("repst") > 0) n_reps_thr = commandLineArgs["repst"].as<uint32_t>();
    if(commandLineArgs.count("repsl") > 0) n_reps_lat = commandLineArgs["repsl"].as<uint32_t>();
    if(commandLineArgs.count("mins") > 0) min_size = commandLineArgs["mins"].as<uint32_t>();
    if(commandLineArgs.count("maxs") > 0) max_size = commandLineArgs["maxs"].as<uint32_t>();
    if(commandLineArgs.count("oper") > 0) oper = commandLineArgs["oper"].as<bool>();

    // uint32_t n_pages = (max_size + hugePageSize - 1) / hugePageSize;
    uint32_t n_pages = ddefSize / hugePageSize + ((ddefSize % hugePageSize > 0) ? 1 : 0);
    uint32_t size = ddefSize;
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
    std::cout << "Number of latency reps: " << n_reps_lat << std::endl;
    
    // Create  queue pairs
    ibvQpMap ictx;
    ictx.addQpair(qpId, targetRegion, ibv_ip, n_pages);
    mstr ? ictx.exchangeQpMaster(port) : ictx.exchangeQpSlave(tcp_mstr_ip.c_str(), port);
    ibvQpConn *iqp = ictx.getQpairConn(qpId);
    cProcess *cproc = iqp->getCProc();


    if (vio) {
        cproc->ioSwitch(IODevs::RDMA_0_HOST_SEND);
    }
 
    uint64_t *hMem = (uint64_t*)iqp->getQpairStruct()->local.vaddr;
    iqp->ibvSync(mstr);

    app_bytes = ddefSize * 65536;

    // Init app layer --------------------------------------------------------------------------------
    struct ibvSge sg;
    struct ibvSendWr wr;
    
    memset(&sg, 0, sizeof(sg));
    sg.type.rdma.local_offs = 0;
    sg.type.rdma.remote_offs = 0;
    sg.type.rdma.len = 8;
    std::cout << "len: " << sg.type.rdma.len << std::endl;

    memset(&wr, 0, sizeof(wr));
    wr.sg_list = &sg;
    wr.num_sge = 1;
    wr.opcode = oper ? IBV_WR_RDMA_WRITE : IBV_WR_RDMA_READ;

    PR_HEADER("RDMA BENCHMARK");
    // Setup
    iqp->ibvClear();
    iqp->ibvSync(mstr);

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
            std::cout << "rng" << std::endl;
            constexpr auto const bram_size = 1024;

            // Initiate
            for(int i = 0; i < n_reps_thr; i++) { // 65536
                uint64_t rng = permute(permute(i) ^ 0x3635) / bram_size;
                memcpy(hMem, &rng, 8);
                iqp->ibvPostSend(&wr);
                // std::cout << i << std::endl;

                // Wait for completion
                while(iqp->ibvDone() < i) { if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  }
                // std::cout << "iqp->ibvDone(): " << iqp->ibvDone() << std::endl;
            }
        };
        auto start_time = std::chrono::high_resolution_clock::now();
        bench.runtime(benchmark_thr);
        auto end_time = std::chrono::high_resolution_clock::now();
        std::cout << std::fixed << std::setprecision(2);
        std::cout << std::setw(8) << app_bytes << " [bytes], thoughput: " 
                    << std::setw(8) << (1000 * app_bytes) / (bench.getAvg()) << " [MB/s], latency: "
                    << ((bench.getAvg()) / 1000) << "us" << std::endl; 

        double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();
        std::cout << "time " << time << "us" << std::endl;
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
            unsigned char outbuf[input_bytes];
#ifdef EN_THR_TESTS
            for(uint32_t n_runs = 1; n_runs <= n_bench_runs; n_runs++) {
                bool k = false;
                // Initiate
                for(int i = 0; i < n_reps_thr; i++) { // 65536

                    // Wait for incoming transactions
                    while(iqp->ibvDone() < i) { if( stalled.load() ) throw std::runtime_error("Stalled, SIGINT caught");  }
                    // std::cout << i << std::endl;

                    // Send back
                    // sleep(1);
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

        } else {
            std::cout << "\e[1mSyncing ...\e[0m" << std::endl;
            iqp->ibvSync(mstr);
        }
    }  

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

    fmt::print("finished\n");
    return EXIT_SUCCESS;
}