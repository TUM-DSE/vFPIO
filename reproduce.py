#!/usr/bin/env python3

import os
import sys
import csv
import json
import time
import copy
import logging
import pathlib
import argparse
import subprocess
from pathlib import Path
from threading import Thread, Timer
from datetime import datetime
from typing import Dict, Iterator, List, Optional, Text, DefaultDict, Any, IO, Callable
# from matplotlib import pyplot as plt

class benchmark:
    def __init__(self, name, bitstream, sw, options=[], sw_2="", options_2=[], prefix_1=[], prefix_2=[], input_size=1024, output_size=1024, repeat=10, app_list=[]):
        self.name = name
        self.bitstream = bitstream
        self.input_size = input_size
        self.output_size = output_size
        self.sw = sw
        self.options = options
        self.sw_2 = sw_2
        self.options_2 = options_2
        self.prefix_1 = prefix_1
        self.prefix_2 = prefix_2
        self.repeat = repeat
        self.app_list = app_list


def average(lst):
    return sum(lst) / len(lst)


def run(
    cmd: List[str],
    extra_env: Dict[str, str] = {},
    stdout: int = subprocess.PIPE,
    input: Optional[str] = None,
    check: bool = True
) -> "subprocess.CompletedProcess[Text]":
    env = os.environ.copy()
    env.update(extra_env)
    env_string = []
    for k, v in extra_env.items():
        env_string.append(f"{k}={v}")
    print(f"$ {' '.join(env_string)} {' '.join(cmd)}")
    return subprocess.run(
        cmd, cwd=ROOT, stdout=stdout, check=check, env=env, text=True, input=input
    )

def remote_cmd(ssh_host: str, args: List[str]) -> None:
    run(["ssh", ssh_host, "--"] + args)


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

def parse_rdma_output(filename):
    # parsing rdma server output
    res = []
    with open(filename, 'r', errors='replace') as file:
        for line in file:
            # print(line.rstrip())
            if line != '':
                line = line.split()
                # print(line)
                # special handling for the TCU abort test
                if "throughput:" in line:
                    # print(line)
                    res.append(float(line[3]))

    print(res)
    logging.info(res)
    print("average: " + str(average(res)) + " MB/s")
    logging.info("average: " + str(average(res)) + " MB/s")

    return res


def reprogram_fpga(bit_path):
    print("reprogramming fpga")
    logging.info("reprogramming fpga")

    cmd = [
        "bash",
        "./program_fpga.sh",
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

def reprogram_fpga_remote(bit_path):
    print("reprogramming fpga remote")
    logging.info("reprogramming fpga remote")

    cmd = [
        "bash",
        "./program_fpga.sh",
        bit_path
    ]
    cmd = ["ssh", "-A", "clara"]
    cmd += ["bash", os.path.join(os.path.realpath("."),  "program_fpga.sh"), bit_path, os.getcwd()]

    print(cmd)
    logging.info(cmd)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True
        )
    except:
        print("Something went wrong during FPGA remote programming. Please check log.")
        exit()

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    logging.info("stdout: %s", result.stdout)
    logging.info("stderr: %s", result.stderr)

    print("FPGA remote program finished. ")



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
                    timeout = 10,
                    check=True,
                )
            except:
                print("Something is wrong with the host application. Please reprogram the FPGA.")
                exit()
        time.sleep(1)

    parse_output(out_file)

    return

def rdma_client(cmd, out_file):

    # print("rdma_client: ")
    # print(cmd)
    with open(out_file, "w+") as f:
        try: 
            client_process = subprocess.run(
                cmd,
                stdout=f,
                stderr=f,
                env=os.environ,
                timeout = 10,
                text = True,
                # check=True,
            )
            # print(client_process.stdout)
        except:
            print("Something is wrong with the rdma client application.")
            exit()


def run_rdma_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bistream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    sw_2_dir = bench_object.sw_2
    options_2 = bench_object.options_2
    prefix_1 = bench_object.prefix_1
    prefix_2 = bench_object.prefix_2

    repeat = bench_object.repeat
    app_list = bench_object.app_list

    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")

    # record experiment data 
    server_file_name = bench_name + "_" + "server_" + timestamp + ".log"
    server_out_file = os.path.join(exp_res_path, server_file_name)

    client_file_name = bench_name + "_" + "client_" + timestamp + ".log"
    client_out_file = os.path.join(exp_res_path, client_file_name)

    cmd = ["sudo"]
    cmd += prefix_1
    cmd += [os.path.join(os.path.realpath("."), sw_dir, "main")]
    cmd += options

    cmd_2 = ["ssh", "-A", "clara", "sudo"]
    cmd_2 += prefix_2
    cmd_2 += [os.path.join(os.path.realpath("."), sw_2_dir, "main")]
    cmd_2 += options_2

    print("Running benchmark: " + bench_name)
    print("bitstream: " + bistream_file)
    # print("cmd: ")
    # print(cmd)
    # print("cmd_2: ")
    # print(cmd_2)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bistream: " + bistream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + server_out_file)

    if reprogram:
        remote_program = Thread(target=reprogram_fpga_remote, args=(bistream_file,))
        remote_program.start()

        reprogram_fpga(bistream_file)
        print('Waiting for the thread...')
        remote_program.join()

        # # reprogram_fpga(bistream_file)
        # reprogram_fpga_remote(bistream_file)
    # exit()
    print("Running server application.")
    print(cmd)

    print("Running client application remotely")
    print(cmd_2)

    with open(server_out_file, "w+") as fs:
        with open(client_out_file, "w+") as fc:

            for i in range(repeat):
                print(i)
                try:
                    server_process = subprocess.Popen(cmd,
                                    stdout = fs, 
                                    stderr = fs,
                                    # stdout = subprocess.PIPE, 
                                    # stderr = subprocess.PIPE,
                                    text = True,
                                    )
                    
                    # client_process = subprocess.run(
                    #     cmd_2,
                    #     stdout=fc,
                    #     stderr=fc,
                    #     env=os.environ,
                    #     timeout = 10,
                    #     text = True,
                    #     # check=True,
                    # )
                    thread = Thread(target=rdma_client, args=(cmd_2, client_out_file))

                    thread.start()

                    # print('Waiting for the thread...')
                    thread.join(timeout=10)

                    output, errors = server_process.communicate()

                    # print("about to kill")
                    server_process.kill()
                    time.sleep(1)
                except:
                    server_process.kill()

    parse_rdma_output(server_out_file)
    return


def pr_client(bench_object, out_file):
    sw_2_dir = bench_object.sw_2
    options_2 = bench_object.options_2
    app_list = bench_object.app_list

    cmd_2 = [
        "sudo",
        os.path.join(os.path.realpath("."), sw_2_dir, "main"),
    ]

    for app in app_list:
        cmd_app = cmd_2 + [app]
        print("cmd_app: ")
        print(cmd_app)
        with open(out_file, "w+") as f:
            try: 
                client_process = subprocess.run(
                    cmd_app,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout = 10,
                    text = True,
                    # check=True,
                )
                print("finished running " + app)
                # print(client_process.stdout)
            except:
                print("Something is wrong with the pr client application.")
                exit()


def run_pr_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bistream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    sw_2_dir = bench_object.sw_2
    options_2 = bench_object.options_2
    repeat = bench_object.repeat
    app_list = bench_object.app_list

    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")

    # record experiment data 
    server_file_name = bench_name + "_" + "server_" + timestamp + ".log"
    server_out_file = os.path.join(exp_res_path, server_file_name)

    client_file_name = bench_name + "_" + "client_" + timestamp + ".log"
    client_out_file = os.path.join(exp_res_path, client_file_name)

    cmd = ["sudo"]
    cmd += options
    cmd += [os.path.join(os.path.realpath("."), sw_dir, "main")]

    cmd_2 = [
        "sudo",
        os.path.join(os.path.realpath("."), sw_2_dir, "main"),
    ]

    print("Running benchmark: " + bench_name)
    print("bistream: " + bistream_file)
    print("cmd: ")
    print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bistream: " + bistream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + server_out_file)

    if reprogram:
        reprogram_fpga(bistream_file)

    print("Running host application.")

    with open(server_out_file, "w+") as f:
        server_process = subprocess.Popen(cmd,
                        stdout = f, 
                        stderr = f,
                        # stdout = subprocess.PIPE, 
                        # stderr = subprocess.PIPE,
                        text = True,
                        )
            
        thread = Thread(target=pr_client, args=(bench_object, client_out_file))

        thread.start()
        output, errors = server_process.communicate()

        print('Waiting for the thread...')
        thread.join()

        print("about to kill")
        server_process.kill()
        # print(output)

    # parse_output(out_file)

    return


def get_data(total, entry, line):
    entry = [entry[0], line[3], round(float(line[3])/total[1]*100, 1), 
                line[7], round(float(line[7])/total[3]*100, 1), 
                float(line[8])+float(line[9])/2, round((float(line[8])+float(line[9])/2)/total[5]*100, 1)]
    return entry

def extract_util(coyote_path, vfpio_path):
    result_table = []
    header = ["", "LUTs", "[%]", "Flips-Flops", "[%]", "BRAM", "[%]"]
    total = ["U280", 1303680, 100.0, 2607360, 100.0, 2016, 100.0]
    result_table.append(header)
    result_table.append(total)

    with open(coyote_path, "r") as f:
        reader = csv.reader(f, delimiter="|")
        for i, line in enumerate(reader):
            entry = []
            if len(line) < 5:
                continue
            for j in range(len(line)):
                line[j] = line[j].strip()
            if line[1] == "cyt_top":
                entry = ["Coyote"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
                break


    with open(vfpio_path, "r") as f:
        reader = csv.reader(f, delimiter="|")
        network_entry = ["Network(RDMA)", 0, 0, 0, 0, 0, 0]
        cdma_entry = ["Local DMA (cdma)", 0, 0, 0, 0, 0, 0]
        scheduler_entry = ["Scheduler", 0, 0, 0, 0, 0, 0]
        vio_entry = ["Virtual IO", 0, 0, 0, 0, 0, 0]

        for i, line in enumerate(reader):
            entry = []
            if len(line) < 5:
                continue
            for j in range(len(line)):
                line[j] = line[j].strip()
            # print(line)
            if line[1] == "cyt_top":
                entry = ["vFPIO"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
            elif line[1] == "inst_network_top_0" or line[1] == "inst_network_top_1":
                network_entry[1] += float(line[3])
                network_entry[3] += float(line[7])
                network_entry[5] += float(line[8])+float(line[9])/2
            elif line[1] == "inst_int_hbm":
                entry = ["Memory"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
            elif line[1] == "xdma_0":
                entry = ["PCIe DMA (xDMA)"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
            elif line[2] == "cdma__parameterized0" or line[2] == "cdma":
                cdma_entry[1] += float(line[3])
                cdma_entry[3] += float(line[7])
                cdma_entry[5] += float(line[8])+float(line[9])/2    
            elif line[0] == "inst_tlb_top":
                entry = ["MMU"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
            elif (line[1] == "inst_hdma_arb_rd" and line[2] == "tlb_arbiter") or line[2] == "tlb_arbiter__parameterized0":
                scheduler_entry[1] += float(line[3])
                scheduler_entry[3] += float(line[7])
                scheduler_entry[5] += float(line[8])+float(line[9])/2
            elif line[1] == "inst_user_wrapper_0":
                vio_entry[1] += float(line[3])
                vio_entry[3] += float(line[7])
                vio_entry[5] += float(line[8])+float(line[9])/2
            elif line[1] == "inst_reg_direct":
                vio_entry[1] -= float(line[3])
                vio_entry[3] -= float(line[7])
                vio_entry[5] -= float(line[8])+float(line[9])/2
    
    network_entry[2] = round(float(network_entry[1])/total[1]*100, 1)
    network_entry[4] = round(float(network_entry[3])/total[3]*100, 1)
    network_entry[6] = round(float(network_entry[5])/total[5]*100, 1)

    cdma_entry[2] = round(float(cdma_entry[1])/total[1]*100, 1)
    cdma_entry[4] = round(float(cdma_entry[3])/total[3]*100, 1)
    cdma_entry[6] = round(float(cdma_entry[5])/total[5]*100, 1)

    scheduler_entry[2] = round(float(scheduler_entry[1])/total[1]*100, 1)
    scheduler_entry[4] = round(float(scheduler_entry[3])/total[3]*100, 1)
    scheduler_entry[6] = round(float(scheduler_entry[5])/total[5]*100, 1)

    vio_entry[2] = round(float(vio_entry[1])/total[1]*100, 1)
    vio_entry[4] = round(float(vio_entry[3])/total[3]*100, 1)
    vio_entry[6] = round(float(vio_entry[5])/total[5]*100, 1)

    result_table.append(network_entry)
    result_table.append(cdma_entry)
    result_table.append(scheduler_entry)
    result_table.append(vio_entry)

    for i in result_table:
        print(i)
    # print(result_table)


def get_data_xlsx(total, entry, line):
    entry = [entry[0], line[1], round(float(line[1])/total[1]*100, 1), 
                line[2], round(float(line[2])/total[3]*100, 1), 
                line[10], round(float(line[10])/total[5]*100, 1)]
    return entry

def extract_util_xlsx(coyote_path, vfpio_path):
    result_table = []
    header = ["", "LUTs", "[%]", "Flips-Flops", "[%]", "BRAM", "[%]"]
    total = ["U280", 1303680, 100.0, 2607360, 100.0, 2016, 100.0]
    result_table.append(header)
    result_table.append(total)

    with open(coyote_path, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            entry = []
            if line == []:
                continue
            if line[0] == "cyt_top":
                entry = ["Static (Coyote)"]
                entry = get_data_xlsx(total, entry, line)
                result_table.append(entry)


    with open(vfpio_path, "r") as f:
        reader = csv.reader(f, delimiter=",")
        network_entry = ["Network(RDMA)", 0, 0, 0, 0, 0, 0]
        cdma_entry = ["Local DMA (cdma)", 0, 0, 0, 0, 0, 0]
        scheduler_entry = ["Scheduler", 0, 0, 0, 0, 0, 0]
        vio_entry = ["Virtual IO", 0, 0, 0, 0, 0, 0]
        for i, line in enumerate(reader):
            entry = []
            if line == []:
                continue
            if line[0] == "cyt_top":
                entry = ["Static (vFPIO)"]
                entry = get_data_xlsx(total, entry, line)
                # entry = ["cyt_top", line[1], round(float(line[1])/total[1]*100, 1), 
                #          line[2], round(float(line[2])/total[3]*100, 1), 
                #          line[10], round(float(line[10])/total[5]*100, 1), 
                #          line[11], round(float(line[11])/total[7]*100, 1)]
                result_table.append(entry)
            elif line[0] == "inst_network_top_0 (network_top)" or line[0] == "inst_network_top_1 (network_top__parameterized0)":
                network_entry[1] += float(line[1])
                network_entry[3] += float(line[2])
                network_entry[5] += float(line[10])
            elif line[0] == "inst_int_hbm (design_hbm)":
                entry = ["Memory"]
                entry = get_data_xlsx(total, entry, line)
                result_table.append(entry)
            elif line[0] == "xdma_0 (design_static_xdma_0_0)":
                entry = ["PCIe DMA (xDMA)"]
                entry = get_data_xlsx(total, entry, line)
                result_table.append(entry)
            elif "cdma__parameterized" in line[0] or "cdma)" in line[0]:
                cdma_entry[1] += float(line[1])
                cdma_entry[3] += float(line[2])
                cdma_entry[5] += float(line[10]) 
            elif line[0] == "inst_tlb_top (tlb_top)":
                entry = ["MMU"]
                entry = get_data_xlsx(total, entry, line)
                result_table.append(entry)
            elif "tlb_arbiter)" in line[0] or "tlb_arbiter__parameterized" in line[0]:
                scheduler_entry[1] += float(line[1])
                scheduler_entry[3] += float(line[2])
                scheduler_entry[5] += float(line[10])
            elif line[0] == "inst_user_wrapper_0 (design_user_wrapper_0)":
                vio_entry[1] += float(line[1])
                vio_entry[3] += float(line[2])
                vio_entry[5] += float(line[10])
            elif "inst_reg_direct" in line[0]:
                vio_entry[1] -= float(line[1])
                vio_entry[3] -= float(line[2])
                vio_entry[5] -= float(line[10])
    
    network_entry[2] = round(float(network_entry[1])/total[1]*100, 1)
    network_entry[4] = round(float(network_entry[3])/total[3]*100, 1)
    network_entry[6] = round(float(network_entry[5])/total[5]*100, 1)

    cdma_entry[2] = round(float(cdma_entry[1])/total[1]*100, 1)
    cdma_entry[4] = round(float(cdma_entry[3])/total[3]*100, 1)
    cdma_entry[6] = round(float(cdma_entry[5])/total[5]*100, 1)

    scheduler_entry[2] = round(float(scheduler_entry[1])/total[1]*100, 1)
    scheduler_entry[4] = round(float(scheduler_entry[3])/total[3]*100, 1)
    scheduler_entry[6] = round(float(scheduler_entry[5])/total[5]*100, 1)

    vio_entry[2] = round(float(vio_entry[1])/total[1]*100, 1)
    vio_entry[4] = round(float(vio_entry[3])/total[3]*100, 1)
    vio_entry[6] = round(float(vio_entry[5])/total[5]*100, 1)

    result_table.append(network_entry)
    result_table.append(cdma_entry)
    result_table.append(scheduler_entry)
    result_table.append(vio_entry)

    print(result_table)



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--reprogram", "-r", action="store_true",
                    help="reprogram fpga before running experiments")
    parser.add_argument("--experiments", "-e", type=str, default="simple", help="select the experiments to run")
    args = parser.parse_args()

    reprogram = args.reprogram

    # Create directory to hold experiment data
    exp_res_path = os.path.join(os.path.realpath("."), "exp-results")
    # pathlib.Path(exp_res_path).mkdir(parents = True, exist_ok = True)

    cmd = ["sudo", "sysctl", "-w", "vm.nr_hugepages=1024"]
    subprocess.run(cmd, capture_output=True, text=True)

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

    rdma_aes_host = benchmark("rdma_aes_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "aes"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_sha256_host = benchmark("rdma_sha256_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw",  
                                ["-w", "1", "--repst", "1", "-o", "sha256"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_md5_host = benchmark("rdma_md5_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "md5"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_nw_host = benchmark("rdma_nw_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "nw"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_matmul_host = benchmark("rdma_matmul_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "mat"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_sha3_host = benchmark("rdma_sha3_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "sha3"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_rng_host = benchmark("rdma_rng_host", "cyt_top_rdma_bram_strm_112", "build_rdma_rng_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "rng"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_gzip_host = benchmark("rdma_gzip_host", "cyt_top_rdma_u280_new_1215", "build_rdma_host_sw", 
                                ["-w", "1", "--repst", "1", "-o", "gzip"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])


    # CLARA -> 
    # sudo FPGA_0_IP_ADDRESS=10.0.0.2 ./main -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i
    # AMY ->  
    # sudo FPGA_0_IP_ADDRESS=10.0.0.1 ./main -t 131.159.102.22 -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i

    # Amy -> 
    # sudo FPGA_0_IP_ADDRESS=10.0.0.1 ./main -w 1 --repst 1 -o nw
    # Clara ->  
    # sudo FPGA_0_IP_ADDRESS=10.0.0.2 ./main -t 131.159.102.20 -w 1 --repst 1 -o nw

    rdma_aes_coyote = benchmark("rdma_aes_coyote", "cyt_top_rdma_aes_u280_strm_1217", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "aes"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_aes_vfpio = benchmark("rdma_aes_vfpio", "cyt_top_rdma_aes_u280_vfpio_1231", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "aes", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_sha256_coyote = benchmark("rdma_sha256_coyote", "cyt_top_rdma_sha256_u280_strm_1218", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "sha256"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_sha256_vfpio = benchmark("rdma_sha256_vfpio", "cyt_top_rdma_sha256_io_104", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "sha256", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_md5_coyote = benchmark("rdma_md5_coyote", "cyt_top_rdma_md5_u280_strm_1218", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "md5"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_md5_vfpio = benchmark("rdma_md5_vfpio", "cyt_top_rdma_md5_io_104", "build_rdma_app_sw",
                               ["-w", "1", "--repst", "1", "-o", "md5"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_nw_coyote = benchmark("rdma_nw_coyote", "cyt_top_rdma_nw_strm_109", "build_rdma_app_sw",
                                ["-w", "1", "--repst", "1", "-o", "nw"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"], repeat = 2)
    rdma_nw_vfpio = benchmark("rdma_nw_vfpio", "cyt_top_rdma_nw_io_109", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "nw", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"], repeat = 2)

    rdma_matmul_coyote = benchmark("rdma_matmul_coyote", "cyt_top_rdma_matmul_strm_109", "build_rdma_app_sw",
                                ["-w", "1", "--repst", "1", "-o", "mat"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_matmul_vfpio = benchmark("rdma_matmul_vfpio", "cyt_top_rdma_matmul_io_109", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "mat", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_sha3_coyote = benchmark("rdma_sha3_coyote", "cyt_top_rdma_keccak_strm_109", "build_rdma_app_sw",
                                ["-w", "1", "--repst", "1", "-o", "sha3"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_sha3_vfpio = benchmark("rdma_sha3_vfpio", "cyt_top_rdma_keccak_io_110", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "sha3", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_rng_coyote = benchmark("rdma_rng_coyote", "cyt_top_rdma_rng_strm_116", "build_rdma_app_sw",
                                ["-w", "1", "--repst", "1", "-o", "rng"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_rng_vfpio = benchmark("rdma_rng_vfpio", "cyt_top_rdma_rng_io_116", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "rng", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])

    rdma_gzip_coyote = benchmark("rdma_gzip_coyote", "cyt_top_rdma_gzip_strm_109", "build_rdma_app_sw",
                                ["-w", "1", "--repst", "1", "-o", "gzip"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])
    rdma_gzip_vfpio = benchmark("rdma_gzip_vfpio", "cyt_top_rdma_gzip_io_109", "build_rdma_app_sw", 
                                ["-w", "1", "--repst", "1", "-o", "gzip", "-i"],
                                "build_rdma_app_sw", ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip", "-i"],
                                prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"], prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"])



    # Partial reconfiguration 
    # in /scratch/chenjiyang/Coyote_faas
    pr_part1_host = benchmark("pr_part1_coyote", "cyt_top_caribou_u280_host_1218", "build_pr_server_sw", 
                                ["BITSTREAM_DIR=" + os.path.join(os.path.realpath("."), "bitstreams/caribou_u280_host")], "build_pr_client_sw", 
                                app_list = ["aes", "nw", "matmul", "sha3", "gzip", "teardown"])
    pr_part2_host = benchmark("pr_part2_coyote", "cyt_top_caribou3_u280_host_1218", "build_pr_server_sw", 
                                ["BITSTREAM_DIR=" + os.path.join(os.path.realpath("."), "bitstreams/caribou3_u280_host")], "build_pr_client_sw", 
                                app_list = ["sha256", "md5", "rng", "teardown"])
    pr_part1_hbm = benchmark("pr_part1_vfpio", "cyt_top_caribou_u280_hbm_1214", "build_pr_server_sw", 
                                ["BITSTREAM_DIR=" + os.path.join(os.path.realpath("."), "bitstreams/caribou_u280_hbm")], "build_pr_client_sw", 
                                app_list = ["aes", "nw", "matmul", "sha3", "gzip", "teardown"])
    pr_part2_hbm = benchmark("pr_part2_vfpio", "cyt_top_caribou3_u280_hbm_1218", "build_pr_server_sw", 
                                ["BITSTREAM_DIR=" + os.path.join(os.path.realpath("."), "bitstreams/caribou3_u280_hbm")], "build_pr_client_sw", 
                                app_list = ["sha256", "md5", "rng", "teardown"])
    
    vfpio_switch = benchmark("md5_vfpio", "cyt_top_md5_io_106", "build_io_app_sw", ["-o", "md5", "-i", "-h", "-f"])
    


    sched_perf_host_coyote = benchmark("sched_perf_host_coyote", "cyt_top_perf_host_strm_0511", "build_perf_host_sw", []);
    sched_perf_host_vfpio = benchmark("sched_perf_host_vfpio", "cyt_top_perf_host_io_0511", "build_perf_host_sw", []);


    # cyt_top_perf_fpga_u280_829_coyote, cyt_top_perf_fpga_u280_829_arbiter
    sched_perf_fpga_coyote = benchmark("sched_perf_fpga_coyote", "cyt_top_perf_fpga_strm_0511", "build_perf_fpga_sw", []);
    sched_perf_fpga_vfpio = benchmark("sched_perf_fpga_vfpio", "cyt_top_perf_fpga_io_0511", "build_perf_fpga_sw", []);
    

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

    Exp_6_1_vfpio_list = {
        "aes_vfpio": aes_vfpio,
        "sha256_vfpio": sha256_vfpio,
        # "md5_vfpio": md5_vfpio,
        # "nw_vfpio": nw_vfpio,
        # "matmul_vfpio": matmul_vfpio,
        # "sha3_vfpio": sha3_vfpio,
        # "rng_vfpio": rng_vfpio,
        # "gzip_vfpio": gzip_vfpio
    }


    Exp_6_1_host_rdma_list = {
        # "aes_vfpio": aes_vfpio,
        # "sha256_vfpio": sha256_vfpio,
        # "md5_vfpio": md5_vfpio,
        # "nw_vfpio": nw_vfpio,
        # "matmul_vfpio": matmul_vfpio,
        # "sha3_vfpio": sha3_vfpio,
        # "rng_vfpio": rng_vfpio,
        # "gzip_vfpio": gzip_vfpio
    }


    Exp_6_1_vfpio_rdma_list = {
        # "rdma_aes_vfpio": rdma_aes_vfpio,
        # "rdma_sha256_vfpio": rdma_sha256_vfpio,
        "rdma_md5_vfpio": rdma_md5_vfpio,
        "rdma_nw_vfpio": rdma_nw_vfpio,
        # "rdma_matmul_vfpio": rdma_matmul_vfpio,
        # "rdma_sha3_vfpio": rdma_sha3_vfpio,
        # "rdma_rng_vfpio": rdma_rng_vfpio,
        "rdma_gzip_vfpio": rdma_gzip_vfpio
    }

    Exp_6_1_coyote_rdma_list = {
        # "rdma_aes_coyote": rdma_aes_coyote,
        # "rdma_sha256_coyote": rdma_sha256_coyote,
        # "rdma_md5_coyote": rdma_md5_coyote,
        "rdma_nw_coyote": rdma_nw_coyote,
        "rdma_matmul_coyote": rdma_matmul_coyote,
        # "rdma_sha3_coyote": rdma_sha3_coyote,
        # "rdma_rng_coyote": rdma_rng_coyote,
        # "rdma_gzip_coyote": rdma_gzip_coyote
    }

    Exp_6_3_host_list = {
        "pr_part1_host": pr_part1_host,
        "pr_part2_host": pr_part2_host,
    }

    Exp_6_3_hmb_list = {
        "pr_part1_hbm": pr_part1_hbm,
        "pr_part2_hbm": pr_part2_hbm,
    }

    Exp_6_3_vfpio_list = {
        "vfpio_switch": vfpio_switch,
    }

    Exp_6_4_2_vfpio_list = {
        # "sched_perf_host_coyote": sched_perf_host_coyote,
        # "sched_perf_host_vfpio": sched_perf_host_vfpio,
        "sched_perf_fpga_coyote": sched_perf_fpga_coyote,
        # "sched_perf_fpga_vfpio": sched_perf_fpga_vfpio,
    }

    Exp_6_5_resource_util = {}

    exp = args.experiments

    if exp == "simple":
        print("Running simple example.")
        # for bench_name, bench_object in simple_list.items():
        # for bench_name, bench_object in Exp_6_1_vfpio_rdma_list.items():
        #     print("--------------------------------------------")
        #     run_rdma_benchmark(exp_res_path, bench_object, reprogram)
        extract_util("util_coyote.csv", "util_test.csv")

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
    elif exp == "Exp_6_1_vfpio_list":
        print("Running Exp_6_1_vfpio_list example.")
        for bench_name, bench_object in Exp_6_1_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_benchmark(exp_res_path, bench_object, reprogram)
    
    elif exp == "Exp_6_3_host_list":
        for bench_name, bench_object in Exp_6_3_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_pr_benchmark(exp_res_path, bench_object ,reprogram)     
    elif exp == "Exp_6_3_hmb_list":
        for bench_name, bench_object in Exp_6_3_hmb_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_pr_benchmark(exp_res_path, bench_object ,reprogram)
    elif exp == "Exp_6_3_vfpio_list":
        for bench_name, bench_object in Exp_6_3_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_pr_benchmark(exp_res_path, bench_object ,reprogram)

    elif exp == "Exp_6_4_2_vfpio_list":
        for bench_name, bench_object in Exp_6_4_2_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            run_pr_benchmark(exp_res_path, bench_object ,reprogram)
    elif exp == "Exp_6_5_resource_util":
        print("--------------------------------------------")
        extract_util("util_coyote.csv", "util_vfpio.csv")

    else:
        # for bench_name, bench_object in Exp_6_1_host_list.items():
        #     # print(bench_object.name)
        #     print("--------------------------------------------")
        #     run_benchmark(exp_res_path, bench_object, reprogram)

        for bench_name, bench_object in Exp_6_4_2_vfpio_list.items():
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
    exp_res_path = os.path.join(os.path.realpath("."), "exp-results")
    pathlib.Path(exp_res_path).mkdir(parents = True, exist_ok = True)

    log_filename = os.path.join(exp_res_path, "log_" + timestamp + ".log")
    logging.basicConfig(level=logging.DEBUG, filename=log_filename, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    main()