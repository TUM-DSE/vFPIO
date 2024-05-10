#include <iostream>
#include <fcntl.h>
#include <unistd.h>
#include <fstream>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <iomanip>

#include "printer.h"
#include "reconfig.h"
#include "cDefs.hpp"

using namespace std::chrono;
using namespace std;

Reconfig::Reconfig(int32_t vfid)
        : vfid(vfid),
          mlock(boost::interprocess::open_or_create, ("vfpga_mtx_mem_0")),// + to_string(vfid)).c_str()),
          plock(boost::interprocess::open_or_create, ("vfpga_mtx_user_ " + to_string(vfid)).c_str())
{
    Printer(vfid)<<"reconfig::reconfig, vfid="<<vfid<<endl;

    // Open
    string region = "/dev/fpga" + to_string(vfid);
    fd = open(region.c_str(), O_RDWR | O_SYNC);
    if (fd == -1) {
        throw runtime_error("failure opening " + region);
    }

    // Cnfg
    uint64_t tmp[2];
    if (ioctl(fd, IOCTL_READ_CNFG, &tmp)) {
        throw runtime_error("ioctl_read_cnfg() failed, vfid: " + to_string(vfid));
    }
    fcnfg.parseCnfg(tmp[0]);

    if (!fcnfg.en_pr) {
        throw runtime_error("PR is not available, EN_PR=" + to_string(fcnfg.en_pr));
    }
}

Reconfig::~Reconfig()
{
    Printer(vfid)<<"reconfig::~reconfig, vfid="<<(int)vfid<<endl;

    // Mapped
    for (auto &it : bstreams)
    {
        removeBitstream(it.first);
    }
    bstreams.clear();

    for (auto &it : mapped_pages)
    {
        freeMem(it.first);
    }
    mapped_pages.clear();

    boost::interprocess::named_mutex::remove(("vfpga_mtx_mem_" + to_string(vfid)).c_str());

    close(fd);
}

// ======-------------------------------------------------------------------------------
// (Thread) Process requests
// ======-------------------------------------------------------------------------------
//    void cSched::processRequests()
//    {
//        unique_lock<mutex> lck_q(mtx_queue);
//        unique_lock<mutex> lck_r(mtx_rcnfg);
//        run = true;
//        bool recIssued = false;
//        int32_t curr_oid = -1;
//        cv_queue.notify_one();
//        lck_q.unlock();
//        lck_r.unlock();
//        ;
//
//        while (run || !request_queue.empty())
//        {
//            lck_q.lock();
//            if (!request_queue.empty())
//            {
//                // Grab next reconfig request
//                auto curr_req = std::move(const_cast<std::unique_ptr<cLoad> &>(request_queue.top()));
//                request_queue.pop();
//                lck_q.unlock();
//
//                // Obtain vFPGA
//                plock.lock();
//
//                // Check whether reconfiguration is needed
//                if (isReconfigurable())
//                {
//                    if (curr_oid != curr_req->oid)
//                    {
//                        reconfigure(curr_req->oid);
//                        recIssued = true;
//                        curr_oid = curr_req->oid;
//                    }
//                    else
//                    {
//                        recIssued = false;
//                    }
//                }
//
//                // Notify
//                lck_r.lock();
//                curr_cpid = curr_req->cpid;
//                curr_run = true;
//                lck_r.unlock();
//                cv_rcnfg.notify_all();
//
//                // Wait for task completion
//                unique_lock<mutex> lck_c(mtx_cmplt);
//                if (cv_cmplt.wait_for(lck_c, cmplTimeout, [=]
//                { return curr_run == false; }))
//                {
//                    syslog(LOG_NOTICE, "Task completed, %s, cpid %d, oid %d, priority %d\n",
//                           (recIssued ? "operator loaded, " : "operator present, "), curr_req->cpid, curr_req->oid, curr_req->priority);
//                }
//                else
//                {
//                    syslog(LOG_NOTICE, "Task failed, cpid %d, oid %d, priority %d\n",
//                           curr_req->cpid, curr_req->oid, curr_req->priority);
//                }
//
//                plock.unlock();
//            }
//            else
//            {
//                lck_q.unlock();
//            }
//
//            nanosleep(&PAUSE, NULL);
//        }
//    }

//    void cSched::pLock(int32_t cpid, int32_t oid, uint32_t priority)
//    {
//        unique_lock<std::mutex> lck_q(mtx_queue);
//        request_queue.emplace(std::unique_ptr<cLoad>(new cLoad{cpid, oid, priority}));
//        lck_q.unlock();
//
//        unique_lock<std::mutex> lck_r(mtx_rcnfg);
//        cv_rcnfg.wait(lck_r, [=]
//        { return ((curr_run == true) && (curr_cpid == cpid)); });
//    }
//
//    void cSched::pUnlock(int32_t cpid)
//    {
//        unique_lock<std::mutex> lck_c(mtx_cmplt);
//        if (curr_cpid == cpid)
//        {
//            curr_run = false;
//            cv_cmplt.notify_one();
//        }
//    }

// ======-------------------------------------------------------------------------------
// Memory management
// ======-------------------------------------------------------------------------------

/**
 * @brief Bitstream memory allocation
 *
 * @param cs_alloc - allocatin config
 * @return void* - pointer to allocated mem
 */
void* Reconfig::getMemForReconfig(const uint32_t n_pages)
{
    Printer(vfid)<<"getMemForReconfig, n_pages="<<n_pages<<endl;

    void *mem = nullptr;
    void *memNonAligned = nullptr;
    uint64_t tmp[2];

    if (n_pages > 0)
    {
        tmp[0] = static_cast<uint64_t>(n_pages);

        mLock();
        auto begin_time = std::chrono::high_resolution_clock::now();

        if (ioctl(fd, IOCTL_ALLOC_HOST_PR_MEM, &tmp))
        {
            mUnlock();
            throw std::runtime_error("ioctl_alloc_host_pr_mem mapping failed");
        }

        memNonAligned = mmap(NULL, (n_pages + 1) * fpga::hugePageSize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, fpga::mmapPr);
        if (memNonAligned == MAP_FAILED)
        {
            mUnlock();
            throw std::runtime_error("get_pr_mem mmap failed");
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        mUnlock();

        mem = (void *)((((reinterpret_cast<uint64_t>(memNonAligned) + fpga::hugePageSize - 1) >> fpga::hugePageShift)) << fpga::hugePageShift);


        mapped_pages.emplace(mem, std::make_pair(csAlloc{CoyoteAlloc::RCNFG_2M, n_pages}, memNonAligned));
        Printer(vfid)<<"Mapped mem at: " << std::hex << reinterpret_cast<uint64_t>(mem) << std::dec<<endl;
        Printer(vfid)<<"Duration: "<<std::chrono::duration_cast<std::chrono::microseconds>(end_time - begin_time).count()<<" µs"<<endl;
    }

    return mem;
}

/**
 * @brief Bitstream memory deallocation
 *
 * @param vaddr - mapped al
 */
void Reconfig::freeMem(void *vaddr)
{
    uint64_t tmp[2];
    uint32_t size;

    tmp[0] = reinterpret_cast<uint64_t>(vaddr);

    if (mapped_pages.find(vaddr) != mapped_pages.end())
    {
        auto mapped = mapped_pages[vaddr];

        switch (mapped.first.alloc)
        {

            case CoyoteAlloc::RCNFG_2M:

                mLock();

                if (munmap(mapped.second, (mapped.first.n_pages + 1) * fpga::hugePageSize) != 0)
                {
                    mUnlock();
                    throw std::runtime_error("free_pr_mem munmap failed");
                }

                if (ioctl(fd, IOCTL_FREE_HOST_PR_MEM, &vaddr))
                {
                    mUnlock();
                    throw std::runtime_error("ioctl_free_host_pr_mem failed");
                }

                mUnlock();

                break;

            default:
                throw std::runtime_error("unauthorized memory deallocation, vfid: " + to_string(vfid));
        }
    }
}

// ======-------------------------------------------------------------------------------
// Reconfiguration
// ======-------------------------------------------------------------------------------

/**
 * @brief Reconfiguration IO
 *
 * @param oid - operator id
 */
void Reconfig::reconfigure(int32_t oid)
{
    if (bstreams.find(oid) != bstreams.end())
    {
        auto bstream = bstreams[oid];
        reconfigure(std::get<0>(bstream), std::get<1>(bstream));
    }
}

/**
 * @brief Reconfiguration IO
 *
 * @param vaddr - bitstream pointer
 * @param len - bitstream length
 */
void Reconfig::reconfigure(void *vaddr, uint32_t len)
{
    uint64_t tmp[2];
    tmp[0] = reinterpret_cast<uint64_t>(vaddr);
    tmp[1] = static_cast<uint64_t>(len);
    auto start_time = std::chrono::high_resolution_clock::now();
    if (ioctl(fd, IOCTL_RECONFIG_LOAD, &tmp)) // Blocking
        throw std::runtime_error("ioctl_reconfig_load failed");
    auto end_time = std::chrono::high_resolution_clock::now();
    double time = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time).count();

    Printer(vfid)<<"Reconfiguration completed, addr="<<std::hex<<vaddr<<", len"<<std::dec<<len<<endl;
    Printer(vfid)<< "Reconfig time " << time/1000 << " ms" << std::endl;
}

/**
 * @brief Add a bitstream to the map
 *
 * @param path - path of the bitstream
 * @param oid - operator ID
 */
void Reconfig::addBitstream(std::string path, int32_t oid)
{
    if (bstreams.find(oid) == bstreams.end())
    {
        // Stream
        ifstream f_bit(path, ios::ate | ios::binary);
        if (!f_bit)
            throw std::runtime_error("Bitstream could not be opened");

        // Size
        uint32_t len = f_bit.tellg();
        f_bit.seekg(0);
        uint32_t n_pages = (len + fpga::hugePageSize - 1) / fpga::hugePageSize;

        // Get mem
        void *vaddr = getMemForReconfig(n_pages);
        uint32_t *vaddr_32 = reinterpret_cast<uint32_t *>(vaddr);

        // Read in
        for (uint32_t i = 0; i < len / 4; i++)
        {
            vaddr_32[i] = 0;
            vaddr_32[i] |= readByte(f_bit) << 24;
            vaddr_32[i] |= readByte(f_bit) << 16;
            vaddr_32[i] |= readByte(f_bit) << 8;
            vaddr_32[i] |= readByte(f_bit);
        }

        Printer(vfid)<<"Bitstream loaded, oid: " << oid<<endl;
        f_bit.close();

        bstreams.insert({oid, std::make_pair(vaddr, len)});
        return;
    }

    throw std::runtime_error("bitstream with same operation ID already present");
}

/**
 * @brief Remove a bitstream from the map
 *
 * @param: oid - Operator ID
 */
void Reconfig::removeBitstream(int32_t oid)
{
    if (bstreams.find(oid) != bstreams.end())
    {
        auto bstream = bstreams[oid];
        freeMem(bstream.first);
    }
}

