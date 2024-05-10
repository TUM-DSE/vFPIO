#!/usr/bin/env python3

import sys
import os
import json
import time
import logging
import pathlib
import argparse
import subprocess
from datetime import datetime
# from matplotlib import pyplot as plt

class benchmark:
    def __init__(self, name, bitstream, sw, options=[], input_size=1024, output_size=1024, repeat=10):
        self.name = name
        self.bitstream = bitstream
        self.input_size = input_size
        self.output_size = output_size
        self.sw = sw
        self.options = options
        self.repeat = repeat

def average(lst):
    return sum(lst) / len(lst)

def parse_output(filename):
    res = []
    with open(filename, 'r', errors='replace') as file:
        for line in file:
            # print(line.rstrip())
            if line != '':
                line = line.split()
                # special handling for the TCU abort test
                if "throughput" in line:
                    # print(line)
                    res.append(float(line[1]))
                    # line = line[6:]

    print(res)
    logging.info(res)
    print("average: " + str(average(res)) + " MB/s")
    logging.info("average: " + str(average(res)) + " MB/s")

    return res

def reprogram_fpga(bit_path):
    print("reprogramming fpga")
    logging.info("reprogramming fpga")
    # TODO: do not use absolute address, but ~/
    cmd = [
        "bash",
        "/home/chenjiyang/program_fpga.sh",
        bit_path
    ]

    print(cmd)
    logging.info(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True
        )
    except:
        print("Something went wrong during FPGA programming. Please check log.")
        exit()

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    logging.info("stdout: %s", result.stdout)
    logging.info("stderr: %s", result.stderr)

    print("FPGA program finished. ")


def run_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bistream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    repeat = bench_object.repeat

    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")

    # record experiment data 
    file_name = bench_name + "_" + timestamp + ".log"
    out_file = os.path.join(exp_res_path, file_name)

    cmd = [
        "sudo",
        os.path.join(os.path.realpath("."), sw_dir, "main"),
    ]
    cmd += options
    print("Running benchmark: " + bench_name)
    print("bistream: " + bistream_file)
    print("cmd: ")
    print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bistream: " + bistream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + out_file)

    if reprogram:
        reprogram_fpga(bistream_file)

    print("Running host application.")
    
    with open(out_file, "w+") as f:
        for i in range(repeat):
            try: 
                subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout = 5,
                    check=True,
                )
            except:
                print("Something is wrong with the host application. Please reprogram the FPGA.")
                exit()
        time.sleep(1)

    parse_output(out_file)

    return

def run_pr_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bistream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    repeat = bench_object.repeat

    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")

    # record experiment data 
    file_name = bench_name + "_" + timestamp + ".log"
    out_file = os.path.join(exp_res_path, file_name)

    cmd = [
        "sudo",
        os.path.join(os.path.realpath("."), sw_dir, "main"),
    ]
    cmd += options
    print("Running benchmark: " + bench_name)
    print("bistream: " + bistream_file)
    print("cmd: ")
    print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bistream: " + bistream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + out_file)

    if reprogram:
        reprogram_fpga(bistream_file)

    print("Running host application.")
    
    with open(out_file, "w+") as f:
        for i in range(repeat):
            try: 
                subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout = 5,
                    check=True,
                )
            except:
                print("Something is wrong with the host application. Please reprogram the FPGA.")
                exit()
        time.sleep(1)

    parse_output(out_file)

    return


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--reprogram", "-r", action="store_true",
                    help="reprogram fpga before running experiments")
    parser.add_argument("--experiments", "-e", type=str, default="simple", help="select the experiments to run")
    args = parser.parse_args()

    reprogram = args.reprogram

    
    # Create directory to hold experiment data
    exp_res_path = os.path.join(os.path.realpath("."), "exp-results")
    pathlib.Path(exp_res_path).mkdir(parents = True, exist_ok = True)


    aes_host = benchmark("aes_host", "cyt_top_host_base_io_112", "build_aes_sha_md5_host_sw", ["-o", "aes"])
    sha256_host = benchmark("sha256_host", "cyt_top_host_base_io_112", "build_aes_sha_md5_host_sw", ["-o", "sha256"])
    md5_host = benchmark("md5_host", "cyt_top_host_base_io_112", "build_aes_sha_md5_host_sw", ["-o", "md5"])
    nw_host = benchmark("nw_host", "cyt_top_host_base_io_112", "build_nw_host_sw", [])
    matmul_host = benchmark("matmul_host", "cyt_top_host_base_io_112", "build_matmul_host_sw", [])
    sha3_host = benchmark("sha3_host", "cyt_top_host_base_io_112", "build_sha3_host_sw", [])
    rng_host = benchmark("rng_host", "cyt_top_bram_app_io_116", "build_rng_host_sw", [])
    gzip_host = benchmark("gzip_host", "cyt_top_host_base_io_112", "build_gzip_host_sw", [])


    # 
    aes_coyote = benchmark("aes_coyote", "cyt_top_aes_hbm_104", "build_io_app_sw", ["-o", "aes", "-h", "-f"], repeat = 2)
    aes_vfpio = benchmark("aes_vfpio", "cyt_top_aes_io_104", "build_io_app_sw", ["-o", "aes", "-i", "-h", "-f"], repeat = 2)

    # 
    sha256_coyote = benchmark("sha256_coyote", "cyt_top_sha256_hbm_104", "build_io_app_sw", ["-o", "sha256", "-h", "-f"], repeat = 2)
    sha256_vfpio = benchmark("sha256_vfpio", "cyt_top_sha256_io_104", "build_io_app_sw", ["-o", "sha256", "-i", "-h", "-f"], repeat = 2)

    # 
    md5_coyote = benchmark("md5_coyote", "cyt_top_md5_hbm_104", "build_io_app_sw", ["-o", "md5", "-h", "-f"])
    md5_vfpio = benchmark("md5_vfpio", "cyt_top_md5_io_106", "build_io_app_sw", ["-o", "md5", "-i", "-h", "-f"])

    # input: 4160 B, output: 16384 B
    nw_coyote = benchmark("nw_coyote", "cyt_top_nw_hbm_104", "build_io_app_sw", ["-o", "nw", "-h", "-f"])
    nw_vfpio = benchmark("nw_vfpio", "cyt_top_nw_io_106", "build_io_app_sw", ["-o", "nw", "-i", "-h", "-f"])

    # input: 65536 B, output: 32768 B
    matmul_coyote = benchmark("matmul_coyote", "cyt_top_matmul_hbm_104", "build_io_app_sw", ["-o", "mat", "-h", "-f"])
    matmul_vfpio = benchmark("matmul_vfpio", "cyt_top_matmul_io_106", "build_io_app_sw", ["-o", "mat", "-i", "-h", "-f"])

    # input: 128 B, output: 64 B
    sha3_coyote = benchmark("sha3_coyote", "cyt_top_keccak_hbm_104", "build_io_app_sw", ["-o", "sha3", "-h", "-f"])
    sha3_vfpio = benchmark("sha3_vfpio", "cyt_top_keccak_io_106", "build_io_app_sw", ["-o", "sha3", "-i", "-h", "-f"])

    # input: 64 B, output: 4095 B
    rng_coyote = benchmark("rng_coyote", "cyt_top_rng_hbm_107", "build_io_app_sw", ["-o", "rng", "-h", "-f"])
    rng_vfpio = benchmark("rng_vfpio", "cyt_top_rng_io_107", "build_io_app_sw", ["-o", "rng", "-i", "-h", "-f"])

    # input: 512 B, output: 128 B
    gzip_coyote = benchmark("gzip_coyote", "cyt_top_gzip_hbm_107", "build_io_app_sw", ["-o", "gzip", "-h", "-f"])
    gzip_vfpio = benchmark("gzip_vfpio", "cyt_top_gzip_io_107", "build_io_app_sw", ["-o", "gzip", "-i", "-h", "-f"])

    # # input: 30720 B, output: 320 B
    # hls4ml_coyote = benchmark("matmul_coyote", "cyt_top_aes_io_104", "build_io_app_sw", ["-o", "aes", "-i", "-h"])
    # hls4ml_vfpio = benchmark("aes_vfpio", "cyt_top_aes_io_104", "build_io_app_sw", ["-o", "aes", "-i", "-h"])


    # RDMA benchmarks

    rdma_aes_host = benchmark("rdma_aes_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_sha256_host = benchmark("rdma_sha256_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_md5_host = benchmark("rdma_md5_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_nw_host = benchmark("rdma_nw_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_matmul_host = benchmark("rdma_matmul_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_sha3_host = benchmark("rdma_sha3_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])
    rdma_rng_host = benchmark("rdma_rng_host", "cyt_top_rdma_u280_new_1215", "build_rdma_rng_host_sw", [])
    rdma_gzip_host = benchmark("rdma_gzip_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", [])



    # CLARA -> 
    # sudo FPGA_0_IP_ADDRESS=10.0.0.2 ./main -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i
    # AMY ->  
    # sudo FPGA_0_IP_ADDRESS=10.0.0.1 ./main -t 131.159.102.22 -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i

    rdma_aes_coyote = benchmark("rdma_aes_coyote", "cyt_top_rdma_aes_u280_strm_1217", "build_rdma_app_sw", ["-o", "aes", "-i", "-h"])
    rdma_aes_vfpio = benchmark("rdma_aes_vfpio", "cyt_top_rdma_aes_u280_vfpio_1231", "build_rdma_app_sw", ["-o", "aes", "-i", "-h"])

    rdma_sha256_coyote = benchmark("rdma_sha256_coyote", "cyt_top_rdma_sha256_u280_strm_1218", "build_rdma_app_sw", [])
    rdma_sha256_vfpio = benchmark("rdma_sha256_vfpio", "cyt_top_rdma_sha256_io_104", "build_rdma_app_sw", [])

    rdma_md5_coyote = benchmark("rdma_md5_coyote", "cyt_top_rdma_md5_u280_strm_1218", "build_rdma_app_sw", [])
    rdma_md5_vfpio = benchmark("rdma_md5_vfpio", "cyt_top_rdma_md5_io_104", "build_rdma_app_sw", [])

    rdma_nw_coyote = benchmark("rdma_nw_coyote", "cyt_top_rdma_nw_strm_109", "build_rdma_app_sw", [])
    rdma_nw_vfpio = benchmark("rdma_nw_vfpio", "cyt_top_rdma_nw_io_109", "build_rdma_app_sw", [])

    rdma_matmul_coyote = benchmark("rdma_matmul_coyote", "cyt_top_rdma_matmul_strm_109", "build_rdma_app_sw", [])
    rdma_matmul_vfpio = benchmark("rdma_matmul_vfpio", "cyt_top_rdma_matmul_io_109", "build_rdma_app_sw", [])

    rdma_sha3_coyote = benchmark("rdma_sha3_coyote", "cyt_top_rdma_keccak_strm_109", "build_rdma_app_sw", [])
    rdma_sha3_vfpio = benchmark("rdma_sha3_vfpio", "cyt_top_rdma_keccak_io_110", "build_rdma_app_sw", [])

    rdma_rng_coyote = benchmark("rdma_rng_coyote", "cyt_top_rdma_rng_strm_116", "build_rdma_app_sw", [])
    rdma_rng_vfpio = benchmark("rdma_rng_vfpio", "cyt_top_rdma_rng_io_116", "build_rdma_app_sw", [])

    rdma_gzip_coyote = benchmark("rdma_gzip_coyote", "cyt_top_rdma_gzip_strm_109", "build_rdma_app_sw", [])
    rdma_gzip_vfpio = benchmark("rdma_gzip_vfpio", "cyt_top_rdma_gzip_io_109", "build_rdma_app_sw", [])



    # Partial reconfiguration 
    # in /scratch/chenjiyang/Coyote_faas
    pr_part1_coyote = benchmark("pr_part1_coyote", "cyt_top_caribou_u280_host_1218", "build_pr_server_sw", "build_pr_client_sw")
    pr_part2_coyote = benchmark("pr_part2_coyote", "cyt_top_caribou3_u280_host_1218", "build_pr_server_sw", "build_pr_client_sw")
    pr_part1_vfpio = benchmark("pr_part1_vfpio", "cyt_top_caribou_u280_hbm_1214", "build_pr_server_sw", "build_pr_client_sw")
    pr_part1_vfpio = benchmark("pr_part1_vfpio", "cyt_top_caribou3_u280_hbm_1218", "build_pr_server_sw", "build_pr_client_sw")
    

    simple_list = {
        "md5_vfpio": md5_vfpio,
    }

    # aes result is wrong
    Exp_6_1_host_list = {
        "aes_host": aes_host,
        "sha256_host": sha256_host,
        "md5_host": md5_host,
        "nw_host": nw_host,
        "matmul_host": matmul_host,
        "sha3_host": sha3_host,
        "rng_host": rng_host,
        "gzip_host": gzip_host,
    }

    Exp_6_1_coyote_list = {
        "aes_coyote": aes_coyote,
        "sha256_coyote": sha256_coyote,
        "md5_coyote": md5_coyote,
        "nw_coyote": nw_coyote,
        "matmul_coyote": matmul_coyote,
        "sha3_coyote": sha3_coyote,
        "rng_coyote": rng_coyote,
        "gzip_coyote": gzip_coyote
    }

    Exp_6_1_vfpga_list = {
        "aes_vfpio": aes_vfpio,
        "sha256_vfpio": sha256_vfpio,
        "md5_vfpio": md5_vfpio,
        "nw_vfpio": nw_vfpio,
        "matmul_vfpio": matmul_vfpio,
        "sha3_vfpio": sha3_vfpio,
        "rng_vfpio": rng_vfpio,
        "gzip_vfpio": gzip_vfpio
    }


    exp = args.experiments

    if exp == "simple":
        print("Running simple example.")
        for bench_name, bench_object in simple_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_benchmark(exp_res_path, bench_object, reprogram)

    elif exp == "Exp_6_1_host_list":
        print("Running Exp_6_1_host_list example.")
        for bench_name, bench_object in Exp_6_1_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_benchmark(exp_res_path, bench_object, reprogram)
    elif exp == "Exp_6_1_coyote_list":
        print("Running Exp_6_1_coyote_list example.")
        for bench_name, bench_object in Exp_6_1_coyote_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_benchmark(exp_res_path, bench_object, reprogram)
    elif exp == "Exp_6_1_vfpga_list":
        print("Running Exp_6_1_vfpga_list example.")
        for bench_name, bench_object in Exp_6_1_vfpga_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_benchmark(exp_res_path, bench_object, reprogram)
    else:
        # for bench_name, bench_object in Exp_6_1_host_list.items():
        #     # print(bench_object.name)
        #     print("--------------------------------------------")
        #     run_benchmark(exp_res_path, bench_object, reprogram)

        for bench_name, bench_object in Exp_6_1_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_pr_benchmark(exp_res_path, bench_object ,reprogram)

    print("--------------------------------------------")
    print("exp result path: " + exp_res_path)

    # parse_output("LICENSE.md")
    print("Finished")

if __name__ == "__main__":
    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")
    log_filename = "log_" + timestamp + ".log"
    logging.basicConfig(level=logging.DEBUG, filename=log_filename, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    main()