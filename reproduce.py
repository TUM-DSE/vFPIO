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
    def __init__(
        self,
        name,
        bitstream,
        sw,
        options=[],
        sw_2="",
        options_2=[],
        prefix_1=[],
        prefix_2=[],
        input_size=1024,
        output_size=1024,
        repeat=5,
        timeout=10,
        app_list=[],
        tags=[],
    ):
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
        self.timeout = timeout
        self.tags = tags


def average(lst):
    return round(sum(lst) / len(lst), 2)


def write_to_file(output_filename, data, tags):
    out = []
    with open(output_filename, "a") as file:
        csvwriter = csv.writer(file)
        out.append(tags[0])
        out.append(tags[1])
        out.extend(data)

        csvwriter.writerow(out)
    print("write finished")


def write_6_3_to_file(output_filename, data, tags, app_list):
    out = []
    # remove the teardown command
    app_list = app_list[:-1]
    # remove potential duplicate data
    if len(data) > len(app_list):
        data = data[1:]
    print(app_list)
    print(data)
    with open(output_filename, "a") as file:
        csvwriter = csv.writer(file)
        for i in range(len(app_list)):
            out = []
            out.append(app_list[i])
            out.append(tags[0])
            out.append(data[i])
            # out.extend(data)

            csvwriter.writerow(out)
    print("write finished")


def write_6_4_1_to_file(output_filename, data, tags):
    out = []
    with open(output_filename, "a") as file:
        csvwriter = csv.writer(file)
        if tags[0] == "RR":
            out.append(tags[0])
            out.extend(data)
            csvwriter.writerow(out)
        elif tags[0] == "vfpio":
            out_hp = ["HP"]
            out_hp.append(data[2])
            out_lp1 = ["LP-1"]
            out_lp1.append(data[0])
            out_lp2 = ["LP-2"]
            out_lp2.append(data[1])

            csvwriter.writerow(out_hp)
            csvwriter.writerow(out_lp1)
            csvwriter.writerow(out_lp2)
    print("write finished")


def write_6_4_1_2_to_file(output_filename, data, tags):
    size_list = ["2", "4", "16", "32"]
    with open(output_filename, "a") as file:
        csvwriter = csv.writer(file)
        for i in range(len(size_list)):
            out = [size_list[i]]
            out.append(data[i] / 1000)
            out.append(tags[0])
            csvwriter.writerow(out)

    print("write finished")


def write_6_4_2_to_file(output_filename, data, tags):
    size_list = ["1", "2", "4", "8", "16", "32", "64", "128", "256"]
    with open(output_filename, "a") as file:
        csvwriter = csv.writer(file)
        for i in range(len(size_list)):
            out = [size_list[i]]
            out.append(data[i])
            out.append(tags[0])
            csvwriter.writerow(out)

    print("write finished")


def parse_6_1_output(filename):
    res = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
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


def parse_6_3_output(filename):
    return parse_6_1_output(filename)


def parse_6_3_pr_output(filename):
    res = []
    res_tmp = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                if "Reconfig_time" in line:
                    # print(line)
                    res_tmp.append(float(line[2]))
    # print("before removing dummy data")
    # print(res_tmp)
    # remove dummy data
    del res_tmp[1::2]

    # print("useful data")
    # print(res_tmp)
    for i in range(len(res_tmp) // 2):
        # print(str(res_tmp[2*i]) + ", " + str(res_tmp[2*i + 1]))
        # res.append((res_tmp[i] + res_tmp[i + 1]) / 2)
        res.append(average([res_tmp[2 * i], res_tmp[2 * i + 1]]))
    # print("final result")
    # print(res)
    logging.info(res)

    return res


def parse_6_3_vio_output(filename):
    res = []
    res_tmp = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                if "io_time" in line:
                    # print(line)
                    res.append(float(line[1]))

    print(res)
    logging.info(res)
    # # print("average: " + str(average(res)) + " MB/s")
    # # logging.info("average: " + str(average(res)) + " MB/s")

    return res


def parse_6_4_1_output(filename):
    res = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                # special handling for the TCU abort test
                if "cycle" in line:
                    # print(line)
                    res.append(float(line[3]))
                    # line = line[6:]

    print(res)
    logging.info(res)
    # print("average: " + str(average(res)) + " MB/s")
    # logging.info("average: " + str(average(res)) + " MB/s")

    return res


def parse_6_4_1_2_output(filename):
    res = []
    res_tmp = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                # special handling for the TCU abort test
                if "Context" in line:
                    # print(line)
                    res_tmp.append(float(line[3]))

    res.append(res_tmp[3] - res_tmp[0])
    res.append(res_tmp[6] - res_tmp[3])
    res.append(res_tmp[9] - res_tmp[6])
    res.append(res_tmp[12] - res_tmp[9])
    print(res)
    logging.info(res)
    # # print("average: " + str(average(res)) + " MB/s")
    # # logging.info("average: " + str(average(res)) + " MB/s")

    return res


def parse_6_4_2_host_output(filename):
    res = []
    res_tmp = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                if "cycle" in line:
                    # print(line)
                    res_tmp.append(float(line[3]))

    for i in range(len(res_tmp) // 3 - 1):
        res.append(average(res_tmp[(i + 1) * 3 : (i + 2) * 3]) / 1000)

    print(res)
    logging.info(res)
    # # print("average: " + str(average(res)) + " MB/s")
    # # logging.info("average: " + str(average(res)) + " MB/s")

    return res


def parse_6_4_2_fpga_output(filename):
    res = []
    res_tmp = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                # print(line)
                if "[cycles]," in line:
                    # print(line)
                    res.append(float(line[6]))

    print(res)
    logging.info(res)

    return res


def parse_rdma_output(filename):
    # parsing rdma server output
    res = []
    with open(filename, "r", errors="replace") as file:
        for line in file:
            # print(line.rstrip())
            if line != "":
                line = line.split()
                print(line)
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

    cmd = ["bash", "./program_fpga.sh", bit_path]

    print(cmd)
    logging.info(cmd)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except:
        print("Something went wrong during FPGA programming. Please check log.")
        result.kill()
        exit()

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    logging.info("stdout: %s", result.stdout)
    logging.info("stderr: %s", result.stderr)

    print("FPGA program finished. ")


def reprogram_fpga_remote(bit_path):
    print("reprogramming fpga remote")
    logging.info("reprogramming fpga remote")

    cmd = ["bash", "./program_fpga.sh", bit_path]
    cmd = ["ssh", "-A", "clara"]
    cmd += [
        "bash",
        os.path.join(os.path.realpath("."), "program_fpga.sh"),
        bit_path,
        os.getcwd(),
    ]

    print(cmd)
    logging.info(cmd)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except:
        print("Something went wrong during FPGA remote programming. Please check log.")
        result.kill()
        exit()

    # print("stdout:", result.stdout)
    # print("stderr:", result.stderr)
    logging.info("stdout: %s", result.stdout)
    logging.info("stderr: %s", result.stderr)

    print("FPGA remote program finished. ")


def run_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bitstream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    repeat = bench_object.repeat
    timeout = bench_object.timeout
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
    print("bitstream: " + bitstream_file)
    print("cmd: ")
    print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bitstream: " + bitstream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + out_file)

    if reprogram:
        reprogram_fpga(bitstream_file)

    print("Running host application.")

    with open(out_file, "w+") as f:
        for i in range(repeat):
            try:
                if bench_name == "rng_host_vfpio":
                    # somehow the rng host version requires running the fpga version twice first to be stable
                    cmd_rng_fpga = cmd + ["-f"]
                    subprocess.run(
                        cmd_rng_fpga,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=os.environ,
                        timeout=timeout,
                        check=True,
                    )

                    subprocess.run(
                        cmd_rng_fpga,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=os.environ,
                        timeout=timeout,
                        check=True,
                    )

                subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout=timeout,
                    check=True,
                )
            except:
                print(
                    "Something is wrong with the host application. Please reprogram the FPGA."
                )
                exit()
        time.sleep(1)

    return out_file


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
                timeout=10,
                text=True,
                # check=True,
            )
            # print(client_process.stdout)
        except:
            print("Something is wrong with the rdma client application.")
            exit()


def run_rdma_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bitstream_file = bench_object.bitstream
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
    print("bitstream: " + bitstream_file)
    # print("cmd: ")
    # print(cmd)
    # print("cmd_2: ")
    # print(cmd_2)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bitstream: " + bitstream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + server_out_file)

    if reprogram:
        remote_program = Thread(target=reprogram_fpga_remote, args=(bitstream_file,))
        remote_program.start()

        reprogram_fpga(bitstream_file)
        print("Waiting for the thread...")
        remote_program.join()

        # # reprogram_fpga(bitstream_file)
        # reprogram_fpga_remote(bitstream_file)
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
                    server_process = subprocess.Popen(
                        cmd,
                        stdout=fs,
                        stderr=fs,
                        # stdout = subprocess.PIPE,
                        # stderr = subprocess.PIPE,
                        text=True,
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
    return server_out_file


def pr_client(bench_object, out_file):
    sw_2_dir = bench_object.sw_2
    options_2 = bench_object.options_2
    app_list = bench_object.app_list[:]
    # somehow the first app is not being recorded in server file
    app_list.insert(0, app_list[0])

    cmd_2 = [
        "sudo",
        os.path.join(os.path.realpath("."), sw_2_dir, "main"),
    ]

    for app in app_list:
        cmd_app = cmd_2 + [app]
        print("\ncmd_app: ")
        print(cmd_app)
        with open(out_file, "w+") as f:
            try:
                client_process = subprocess.run(
                    cmd_app,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout=10,
                    text=True,
                    # check=True,
                )
                # print("finished running " + app)
                # print(client_process.stdout)
            except:
                print("Something is wrong with the pr client application.")
                exit()


def run_pr_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bitstream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options

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

    print("Running benchmark: " + bench_name)
    print("bitstream: " + bitstream_file)
    print("cmd: ")
    print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bitstream: " + bitstream_file)
    logging.info("cmd: ")
    logging.info(cmd)
    print("output file: " + server_out_file)

    if reprogram:
        reprogram_fpga(bitstream_file)

    print("Running host application.")

    with open(server_out_file, "w+") as f:
        try:
            server_process = subprocess.Popen(
                cmd,
                stdout=f,
                stderr=f,
                # stdout = subprocess.PIPE,
                # stderr = subprocess.PIPE,
                text=True,
            )

            thread = Thread(target=pr_client, args=(bench_object, client_out_file))

            thread.start()
            output, errors = server_process.communicate()

            print("Waiting for the thread...")
            thread.join()

            print("about to kill")
            server_process.kill()
            # print(output)
        except:
            server_process.kill()

    # parse_output(out_file)

    return server_out_file


def run_cntx_benchmark(exp_res_path, bench_object, reprogram):
    # process benchmark related data

    bench_name = bench_object.name
    bitstream_file = bench_object.bitstream
    sw_dir = bench_object.sw
    options = bench_object.options
    repeat = bench_object.repeat
    app_list = bench_object.app_list

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
    print("bitstream: " + bitstream_file)
    # print("cmd: ")
    # print(cmd)

    logging.info("Running benchmark: " + bench_name)
    logging.info("bitstream: " + bitstream_file)
    # logging.info("cmd: ")
    # logging.info(cmd)
    print("output file: " + out_file)

    if reprogram:
        reprogram_fpga(bitstream_file)

    print("Running host application.")

    with open(out_file, "w+") as f:
        for size in app_list:
            # "-s", "16384", "-e", "16384"
            cmd_size = cmd + ["-s", size, "-e", size]
            print("cmd: ")
            print(cmd_size)
            try:
                subprocess.run(
                    cmd_size,
                    stdout=f,
                    stderr=f,
                    env=os.environ,
                    timeout=10,
                    check=True,
                )
            except:
                print(
                    "Something is wrong with the host application. Please reprogram the FPGA."
                )
                exit()
        time.sleep(1)

    return out_file


def get_data(total, entry, line):
    entry = [
        entry[0],
        line[3],
        round(float(line[3]) / total[1] * 100, 1),
        line[7],
        round(float(line[7]) / total[3] * 100, 1),
        float(line[8]) + float(line[9]) / 2,
        round((float(line[8]) + float(line[9]) / 2) / total[5] * 100, 1),
    ]
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
                network_entry[5] += float(line[8]) + float(line[9]) / 2
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
                cdma_entry[5] += float(line[8]) + float(line[9]) / 2
            elif line[0] == "inst_tlb_top":
                entry = ["MMU"]
                entry = get_data(total, entry, line)
                result_table.append(entry)
            elif (line[1] == "inst_hdma_arb_rd" and line[2] == "tlb_arbiter") or line[
                2
            ] == "tlb_arbiter__parameterized0":
                scheduler_entry[1] += float(line[3])
                scheduler_entry[3] += float(line[7])
                scheduler_entry[5] += float(line[8]) + float(line[9]) / 2
            # elif line[1] == "inst_user_wrapper_0":
            #     vio_entry[1] += float(line[3])
            #     vio_entry[3] += float(line[7])
            #     vio_entry[5] += float(line[8]) + float(line[9]) / 2
            # elif line[1] == "inst_reg_direct":
            #     vio_entry[1] -= float(line[3])
            #     vio_entry[3] -= float(line[7])
            #     vio_entry[5] -= float(line[8]) + float(line[9]) / 2
            elif line[1] == "(inst_user_c0_0)":
                vio_entry = ["Virtual IO"]
                vio_entry = get_data(total, vio_entry, line)
                # print(line)

    network_entry[2] = round(float(network_entry[1]) / total[1] * 100, 1)
    network_entry[4] = round(float(network_entry[3]) / total[3] * 100, 1)
    network_entry[6] = round(float(network_entry[5]) / total[5] * 100, 1)

    cdma_entry[2] = round(float(cdma_entry[1]) / total[1] * 100, 1)
    cdma_entry[4] = round(float(cdma_entry[3]) / total[3] * 100, 1)
    cdma_entry[6] = round(float(cdma_entry[5]) / total[5] * 100, 1)

    scheduler_entry[2] = round(float(scheduler_entry[1]) / total[1] * 100, 1)
    scheduler_entry[4] = round(float(scheduler_entry[3]) / total[3] * 100, 1)
    scheduler_entry[6] = round(float(scheduler_entry[5]) / total[5] * 100, 1)

    # vio_entry[2] = round(float(vio_entry[1]) / total[1] * 100, 1)
    # vio_entry[4] = round(float(vio_entry[3]) / total[3] * 100, 1)
    # vio_entry[6] = round(float(vio_entry[5]) / total[5] * 100, 1)

    result_table.append(network_entry)
    result_table.append(cdma_entry)
    result_table.append(scheduler_entry)
    result_table.append(vio_entry)

    for i in result_table:
        print(i)
    # print(result_table)


def get_data_xlsx(total, entry, line):
    entry = [
        entry[0],
        line[1],
        round(float(line[1]) / total[1] * 100, 1),
        line[2],
        round(float(line[2]) / total[3] * 100, 1),
        line[10],
        round(float(line[10]) / total[5] * 100, 1),
    ]
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
            elif (
                line[0] == "inst_network_top_0 (network_top)"
                or line[0] == "inst_network_top_1 (network_top__parameterized0)"
            ):
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

    network_entry[2] = round(float(network_entry[1]) / total[1] * 100, 1)
    network_entry[4] = round(float(network_entry[3]) / total[3] * 100, 1)
    network_entry[6] = round(float(network_entry[5]) / total[5] * 100, 1)

    cdma_entry[2] = round(float(cdma_entry[1]) / total[1] * 100, 1)
    cdma_entry[4] = round(float(cdma_entry[3]) / total[3] * 100, 1)
    cdma_entry[6] = round(float(cdma_entry[5]) / total[5] * 100, 1)

    scheduler_entry[2] = round(float(scheduler_entry[1]) / total[1] * 100, 1)
    scheduler_entry[4] = round(float(scheduler_entry[3]) / total[3] * 100, 1)
    scheduler_entry[6] = round(float(scheduler_entry[5]) / total[5] * 100, 1)

    vio_entry[2] = round(float(vio_entry[1]) / total[1] * 100, 1)
    vio_entry[4] = round(float(vio_entry[3]) / total[3] * 100, 1)
    vio_entry[6] = round(float(vio_entry[5]) / total[5] * 100, 1)

    result_table.append(network_entry)
    result_table.append(cdma_entry)
    result_table.append(scheduler_entry)
    result_table.append(vio_entry)

    print(result_table)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reprogram",
        "-r",
        action="store_true",
        help="reprogram fpga before running experiments",
    )
    parser.add_argument(
        "--experiments",
        "-e",
        type=str,
        default="simple",
        help="select the experiments to run",
    )
    args = parser.parse_args()

    reprogram = args.reprogram

    # Create directory to hold experiment data
    exp_res_path = os.path.join(os.path.realpath("."), "exp-results")
    # pathlib.Path(exp_res_path).mkdir(parents = True, exist_ok = True)

    cmd = ["sudo", "sysctl", "-w", "vm.nr_hugepages=1024"]
    subprocess.run(cmd, capture_output=True, text=True)

    aes_host = benchmark(
        "aes_host",
        "cyt_top_host_base_io_112",
        "build_aes_sha_md5_host_sw",
        ["-o", "aes"],
        tags=["aes", "Host"],
    )
    sha256_host = benchmark(
        "sha256_host",
        "cyt_top_host_base_io_112",
        "build_aes_sha_md5_host_sw",
        ["-o", "sha256"],
        tags=["sha256", "Host"],
    )
    md5_host = benchmark(
        "md5_host",
        "cyt_top_host_base_io_112",
        "build_aes_sha_md5_host_sw",
        ["-o", "md5"],
        tags=["md5", "Host"],
    )
    nw_host = benchmark(
        "nw_host",
        "cyt_top_host_base_io_112",
        "build_nw_host_sw",
        [],
        tags=["nw", "Host"],
    )
    matmul_host = benchmark(
        "matmul_host",
        "cyt_top_host_base_io_112",
        "build_matmul_host_sw",
        [],
        tags=["matmul", "Host"],
    )
    sha3_host = benchmark(
        "sha3_host",
        "cyt_top_host_base_io_112",
        "build_sha3_host_sw",
        [],
        tags=["sha3", "Host"],
    )
    rng_host = benchmark(
        "rng_host",
        "cyt_top_bram_app_io_116",
        "build_rng_host_sw",
        [],
        timeout=18,
        tags=["rng", "Host"],
    )
    gzip_host = benchmark(
        "gzip_host",
        "cyt_top_host_base_io_112",
        "build_gzip_host_sw",
        [],
        tags=["gzip", "Host"],
    )

    #
    aes_coyote = benchmark(
        "aes_coyote",
        "cyt_top_aes_hbm_104",
        "build_io_app_sw",
        ["-o", "aes", "-h", "-f"],
        repeat=2,
        tags=["aes", "Coyote"],
    )
    aes_host_coyote = benchmark(
        "aes_host_coyote",
        "cyt_top_aes_u280_strm_1206",
        "build_io_app_sw",
        ["-o", "aes", "-h"],
        repeat=2,
        tags=["aes", "Coyote"],
    )
    aes_vfpio = benchmark(
        "aes_vfpio",
        "cyt_top_aes_io_104",
        "build_io_app_sw",
        ["-o", "aes", "-i", "-h", "-f"],
        repeat=2,
        tags=["aes", "vFPIO"],
    )
    aes_host_vfpio = benchmark(
        "aes_host_vfpio",
        "cyt_top_aes_io_104",
        "build_io_app_sw",
        ["-o", "aes", "-i", "-h"],
        repeat=2,
        tags=["aes", "vFPIO"],
    )

    #
    sha256_coyote = benchmark(
        "sha256_coyote",
        "cyt_top_sha256_hbm_104",
        "build_io_app_sw",
        ["-o", "sha256", "-h", "-f"],
        repeat=2,
        tags=["sha256", "Coyote"],
    )
    sha256_host_coyote = benchmark(
        "sha256_host_coyote",
        "cyt_top_sha256_u280_strm_1206",
        "build_io_app_sw",
        ["-o", "sha256", "-h"],
        repeat=1,
        tags=["sha256", "Coyote"],
    )
    sha256_vfpio = benchmark(
        "sha256_vfpio",
        "cyt_top_sha256_io_104",
        "build_io_app_sw",
        ["-o", "sha256", "-i", "-h", "-f"],
        repeat=2,
        tags=["sha256", "vFPIO"],
    )
    sha256_host_vfpio = benchmark(
        "sha256_host_vfpio",
        "cyt_top_sha256_io_104",
        "build_io_app_sw",
        ["-o", "sha256", "-i", "-h"],
        repeat=1,
        tags=["sha256", "vFPIO"],
    )

    #
    md5_coyote = benchmark(
        "md5_coyote",
        "cyt_top_md5_hbm_104",
        "build_io_app_sw",
        ["-o", "md5", "-h", "-f"],
        tags=["md5", "Coyote"],
    )
    md5_host_coyote = benchmark(
        "md5_host_coyote",
        "cyt_top_md5_u280_strm_1206",
        "build_io_app_sw",
        ["-o", "md5", "-h"],
        repeat=1,
        tags=["md5", "Coyote"],
    )
    md5_vfpio = benchmark(
        "md5_vfpio",
        "cyt_top_md5_io_106",
        "build_io_app_sw",
        ["-o", "md5", "-i", "-h", "-f"],
        tags=["md5", "vFPIO"],
    )
    md5_host_vfpio = benchmark(
        "md5_host_vfpio",
        "cyt_top_md5_io_106",
        "build_io_app_sw",
        ["-o", "md5", "-i", "-h"],
        repeat=1,
        tags=["md5", "vFPIO"],
    )

    # input: 4160 B, output: 16384 B
    nw_coyote = benchmark(
        "nw_coyote",
        "cyt_top_nw_hbm_104",
        "build_io_app_sw",
        ["-o", "nw", "-h", "-f"],
        tags=["nw", "Coyote"],
    )
    nw_host_coyote = benchmark(
        "nw_host_coyote",
        "cyt_top_nw_u280_strm_1108",
        "build_io_app_sw",
        ["-o", "nw", "-h"],
        tags=["nw", "Coyote"],
    )
    nw_vfpio = benchmark(
        "nw_vfpio",
        "cyt_top_nw_io_106",
        "build_io_app_sw",
        ["-o", "nw", "-i", "-h", "-f"],
        tags=["nw", "vFPIO"],
    )
    nw_host_vfpio = benchmark(
        "nw_host_vfpio",
        "cyt_top_nw_io_106",
        "build_io_app_sw",
        ["-o", "nw", "-i", "-h"],
        tags=["nw", "vFPIO"],
    )

    # input: 65536 B, output: 32768 B
    matmul_coyote = benchmark(
        "matmul_coyote",
        "cyt_top_matmul_hbm_104",
        "build_io_app_sw",
        ["-o", "mat", "-h", "-f"],
        tags=["matmul", "Coyote"],
    )
    matmul_host_coyote = benchmark(
        "matmul_host_coyote",
        "cyt_top_matmul_u280_dram_1124",
        "build_io_app_sw",
        ["-o", "mat", "-h"],
        tags=["matmul", "Coyote"],
    )
    matmul_vfpio = benchmark(
        "matmul_vfpio",
        "cyt_top_matmul_io_106",
        "build_io_app_sw",
        ["-o", "mat", "-i", "-h", "-f"],
        tags=["matmul", "vFPIO"],
    )
    matmul_host_vfpio = benchmark(
        "matmul_host_vfpio",
        "cyt_top_matmul_io_106",
        "build_io_app_sw",
        ["-o", "mat", "-i", "-h"],
        tags=["matmul", "vFPIO"],
    )

    # input: 128 B, output: 64 B
    sha3_coyote = benchmark(
        "sha3_coyote",
        "cyt_top_keccak_hbm_104",
        "build_io_app_sw",
        ["-o", "sha3", "-h", "-f"],
        tags=["sha3", "Coyote"],
    )
    sha3_host_coyote = benchmark(
        "sha3_host_coyote",
        "cyt_top_keccak_u280_dram_1124",
        "build_io_app_sw",
        ["-o", "sha3", "-h"],
        tags=["sha3", "Coyote"],
    )
    sha3_vfpio = benchmark(
        "sha3_vfpio",
        "cyt_top_keccak_io_106",
        "build_io_app_sw",
        ["-o", "sha3", "-i", "-h", "-f"],
        tags=["sha3", "vFPIO"],
    )
    sha3_host_vfpio = benchmark(
        "sha3_host_vfpio",
        "cyt_top_keccak_io_106",
        "build_io_app_sw",
        ["-o", "sha3", "-i", "-h"],
        tags=["sha3", "vFPIO"],
    )

    # input: 64 B, output: 4095 B
    rng_coyote = benchmark(
        "rng_coyote",
        "cyt_top_rng_hbm_107",
        "build_io_app_sw",
        ["-o", "rng", "-h", "-f"],
        tags=["rng", "Coyote"],
    )
    rng_host_coyote = benchmark(
        "rng_host_coyote",
        "cyt_top_rng_u280_strm_1117",
        "build_io_app_sw",
        ["-o", "rng", "-h"],
        tags=["rng", "Coyote"],
    )
    rng_vfpio = benchmark(
        "rng_vfpio",
        "cyt_top_rng_io_107",
        "build_io_app_sw",
        ["-o", "rng", "-i", "-h", "-f"],
        tags=["rng", "vFPIO"],
    )
    rng_host_vfpio = benchmark(
        "rng_host_vfpio",
        "cyt_top_rng_io_107",
        "build_io_app_sw",
        ["-o", "rng", "-i", "-h"],
        tags=["rng", "vFPIO"],
    )

    # input: 512 B, output: 128 B
    gzip_coyote = benchmark(
        "gzip_coyote",
        "cyt_top_gzip_hbm_107",
        "build_io_app_sw",
        ["-o", "gzip", "-h", "-f"],
        tags=["gzip", "Coyote"],
    )
    gzip_host_coyote = benchmark(
        "gzip_host_coyote",
        "cyt_top_gzip_u280_strm_1116",
        "build_io_app_sw",
        ["-o", "gzip", "-h"],
        tags=["gzip", "Coyote"],
    )
    gzip_vfpio = benchmark(
        "gzip_vfpio",
        "cyt_top_gzip_io_107",
        "build_io_app_sw",
        ["-o", "gzip", "-i", "-h", "-f"],
        tags=["gzip", "vFPIO"],
    )
    gzip_host_vfpio = benchmark(
        "gzip_host_vfpio",
        "cyt_top_gzip_io_107",
        "build_io_app_sw",
        ["-o", "gzip", "-i", "-h"],
        tags=["gzip", "vFPIO"],
    )

    # # input: 30720 B, output: 320 B
    # hls4ml_coyote = benchmark("matmul_coyote", "cyt_top_aes_io_104", "build_io_app_sw", ["-o", "aes", "-i", "-h"])
    # hls4ml_vfpio = benchmark("aes_vfpio", "cyt_top_aes_io_104", "build_io_app_sw", ["-o", "aes", "-i", "-h"])

    # RDMA benchmarks

    rdma_aes_host = benchmark(
        "rdma_aes_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "aes"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["aes", "rdma_host"],
    )
    rdma_sha256_host = benchmark(
        "rdma_sha256_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "sha256"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha256", "rdma_host"],
    )
    rdma_md5_host = benchmark(
        "rdma_md5_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "md5"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["md5", "rdma_host"],
    )
    rdma_nw_host = benchmark(
        "rdma_nw_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "nw"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["nw", "rdma_host"],
    )
    rdma_matmul_host = benchmark(
        "rdma_matmul_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "mat"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["mat", "rdma_host"],
    )
    rdma_sha3_host = benchmark(
        "rdma_sha3_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "sha3"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha3", "rdma_host"],
    )
    rdma_rng_host = benchmark(
        "rdma_rng_host",
        "cyt_top_rdma_bram_strm_112",
        "build_rdma_rng_host_sw",
        ["-w", "1", "--repst", "1", "-o", "rng"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["rng", "rdma_host"],
    )
    rdma_gzip_host = benchmark(
        "rdma_gzip_host",
        "cyt_top_rdma_u280_new_1215",
        "build_rdma_host_sw",
        ["-w", "1", "--repst", "1", "-o", "gzip"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["gzip", "rdma_host"],
    )

    # CLARA ->
    # sudo FPGA_0_IP_ADDRESS=10.0.0.2 ./main -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i
    # AMY ->
    # sudo FPGA_0_IP_ADDRESS=10.0.0.1 ./main -t 131.159.102.22 -w 1 --maxs 65536 --mins 65536 --repsl 100 --repst 1 -o mat -i

    # Amy ->
    # sudo FPGA_0_IP_ADDRESS=10.0.0.1 ./main -w 1 --repst 1 -o nw
    # Clara ->
    # sudo FPGA_0_IP_ADDRESS=10.0.0.2 ./main -t 131.159.102.20 -w 1 --repst 1 -o nw

    rdma_aes_coyote = benchmark(
        "rdma_aes_coyote",
        "cyt_top_rdma_aes_u280_strm_1217",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "aes"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["aes", "rdma_coyote"],
    )
    rdma_aes_vfpio = benchmark(
        "rdma_aes_vfpio",
        "cyt_top_rdma_aes_u280_vfpio_1231",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "aes", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "aes", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["aes", "rdma_vfpio"],
    )

    rdma_sha256_coyote = benchmark(
        "rdma_sha256_coyote",
        "cyt_top_rdma_sha256_u280_strm_1218",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "sha256"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha256", "rdma_coyote"],
    )
    rdma_sha256_vfpio = benchmark(
        "rdma_sha256_vfpio",
        "cyt_top_rdma_sha256_io_104",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "sha256", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha256", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha256", "rdma_vfpio"],
    )

    rdma_md5_coyote = benchmark(
        "rdma_md5_coyote",
        "cyt_top_rdma_md5_u280_strm_1218",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "md5"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["md5", "rdma_coyote"],
    )
    rdma_md5_vfpio = benchmark(
        "rdma_md5_vfpio",
        "cyt_top_rdma_md5_io_104",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "md5"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "md5", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["md5", "rdma_vfpio"],
    )

    rdma_nw_coyote = benchmark(
        "rdma_nw_coyote",
        "cyt_top_rdma_nw_strm_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "nw"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        repeat=2,
        tags=["nw", "rdma_coyote"],
    )
    rdma_nw_vfpio = benchmark(
        "rdma_nw_vfpio",
        "cyt_top_rdma_nw_io_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "nw", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "nw", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        repeat=2,
        tags=["nw", "rdma_vfpio"],
    )

    rdma_matmul_coyote = benchmark(
        "rdma_matmul_coyote",
        "cyt_top_rdma_matmul_strm_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "mat"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["matmul", "rdma_coyote"],
    )
    rdma_matmul_vfpio = benchmark(
        "rdma_matmul_vfpio",
        "cyt_top_rdma_matmul_io_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "mat", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "mat", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["matmul", "rdma_vfpio"],
    )

    rdma_sha3_coyote = benchmark(
        "rdma_sha3_coyote",
        "cyt_top_rdma_keccak_strm_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "sha3"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha3", "rdma_coyote"],
    )
    rdma_sha3_vfpio = benchmark(
        "rdma_sha3_vfpio",
        "cyt_top_rdma_keccak_io_110",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "sha3", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "sha3", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["sha3", "rdma_vfpio"],
    )

    rdma_rng_coyote = benchmark(
        "rdma_rng_coyote",
        "cyt_top_rdma_rng_strm_116",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "rng"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["rng", "rdma_coyote"],
    )
    rdma_rng_vfpio = benchmark(
        "rdma_rng_vfpio",
        "cyt_top_rdma_rng_io_116",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "rng", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "rng", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["rng", "rdma_vfpio"],
    )

    rdma_gzip_coyote = benchmark(
        "rdma_gzip_coyote",
        "cyt_top_rdma_gzip_strm_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "gzip"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["gzip", "rdma_coyote"],
    )
    rdma_gzip_vfpio = benchmark(
        "rdma_gzip_vfpio",
        "cyt_top_rdma_gzip_io_109",
        "build_rdma_app_sw",
        ["-w", "1", "--repst", "1", "-o", "gzip", "-i"],
        "build_rdma_app_sw",
        ["-t", "131.159.102.20", "-w", "1", "--repst", "1", "-o", "gzip", "-i"],
        prefix_1=["FPGA_0_IP_ADDRESS=10.0.0.1"],
        prefix_2=["FPGA_0_IP_ADDRESS=10.0.0.2"],
        tags=["gzip", "rdma_vfpio"],
    )

    # Partial reconfiguration
    # in /scratch/chenjiyang/Coyote_faas
    pr_part1_host = benchmark(
        "pr_part1_coyote",
        "cyt_top_caribou_u280_host_1218",
        "build_pr_server_sw",
        [
            "BITSTREAM_DIR="
            + os.path.join(os.path.realpath("."), "bitstreams/caribou_u280_host")
        ],
        "build_pr_client_sw",
        app_list=["aes", "nw", "matmul", "sha3", "gzip", "teardown"],
        tags=["host"],
    )
    pr_part2_host = benchmark(
        "pr_part2_coyote",
        "cyt_top_caribou3_u280_host_1218",
        "build_pr_server_sw",
        [
            "BITSTREAM_DIR="
            + os.path.join(os.path.realpath("."), "bitstreams/caribou3_u280_host")
        ],
        "build_pr_client_sw",
        app_list=["sha256", "md5", "rng", "teardown"],
        tags=["host"],
    )
    # app_list = ["sha256", "md5", "rng", "teardown"])
    pr_part1_hbm = benchmark(
        "pr_part1_vfpio",
        "cyt_top_caribou_u280_hbm_1214",
        "build_pr_server_sw",
        [
            "BITSTREAM_DIR="
            + os.path.join(os.path.realpath("."), "bitstreams/caribou_u280_hbm")
        ],
        "build_pr_client_sw",
        app_list=["aes", "nw", "matmul", "sha3", "gzip", "teardown"],
        tags=["hbm"],
    )
    pr_part2_hbm = benchmark(
        "pr_part2_vfpio",
        "cyt_top_caribou3_u280_hbm_1218",
        "build_pr_server_sw",
        [
            "BITSTREAM_DIR="
            + os.path.join(os.path.realpath("."), "bitstreams/caribou3_u280_hbm")
        ],
        "build_pr_client_sw",
        app_list=["sha256", "md5", "rng", "teardown"],
        tags=["hbm"],
    )
    # app_list = ["sha256", "md5", "rng", "teardown"])

    vfpio_switch = benchmark(
        "vfpio_switch", "cyt_top_md5_io_106", "build_io_switch_time_sw", [], repeat=1
    )

    # sudo ./main -r 100 -s 16384 -e 16384 -p 2
    sched_perf_host_coyote_cycle = benchmark(
        "sched_perf_host_coyote_cycle",
        "cyt_top_perf_host_io_ila_0515",
        "build_perf_host_arbiter_sw",
        ["-r", "100", "-s", "16384", "-e", "16384"],
        repeat=1,
        tags=["RR"],
    )
    sched_perf_host_vfpio_cycle = benchmark(
        "sched_perf_host_vfpio_cycle",
        "cyt_top_perf_host_io_ila_0515",
        "build_perf_host_arbiter_sw",
        ["-r", "100", "-s", "16384", "-e", "16384", "-p", "2"],
        repeat=1,
        tags=["vFPIO"],
    )

    # sudo ./main -r 100 -s 16384 -e 16384 -p 2
    sched_perf_host_coyote_cntx = benchmark(
        "sched_perf_host_coyote_cntx",
        "cyt_top_perf_host_io_ila_0515",
        "build_perf_host_arbiter_sw",
        ["-r", "100"],
        repeat=1,
        app_list=["1024", "2048", "4096", "8192", "16384", "32768"],
        tags=["Coyote"],
    )
    sched_perf_host_vfpio_cntx = benchmark(
        "sched_perf_host_vfpio_cntx",
        "cyt_top_perf_host_io_ila_0515",
        "build_perf_host_arbiter_sw",
        ["-r", "100", "-p", "2"],
        repeat=1,
        app_list=["1024", "2048", "4096", "8192", "16384", "32768"],
        tags=["vFPIO"],
    )

    # cyt_top_perf_fpga_u280_829_coyote, cyt_top_perf_fpga_u280_829_arbiter
    # sudo ./main -r 100 -s 1024 -e 262144
    sched_perf_host_coyote = benchmark(
        "sched_perf_host_coyote",
        "cyt_top_perf_host_strm_0520",
        "build_perf_host_arbiter_sw",
        ["-r", "100"],
        repeat=1,
        app_list=[
            "1024",
            "1024",
            "2048",
            "4096",
            "8192",
            "16384",
            "32768",
            "65536",
            "131072",
            "262144",
        ],
        tags=["Coyote"],
    )
    sched_perf_host_vfpio = benchmark(
        "sched_perf_host_vfpio",
        "cyt_top_perf_host_io_ila_0515",
        "build_perf_host_arbiter_sw",
        ["-r", "100"],
        repeat=1,
        app_list=[
            "1024",
            "1024",
            "2048",
            "4096",
            "8192",
            "16384",
            "32768",
            "65536",
            "131072",
            "262144",
        ],
        tags=["vFPIO"],
    )
    # ["-r", "100", "-p", "2"], repeat=1, app_list = ["1024", "1024", "2048", "4096", "8192", "16384", "32768", "65536", "131072", "262144"])

    # cyt_top_perf_fpga_u280_829_coyote, cyt_top_perf_fpga_u280_829_arbiter
    # sudo ./main -r 100 -s 1024 -e 1024
    sched_perf_fpga_coyote = benchmark(
        "sched_perf_fpga_coyote",
        "cyt_top_perf_fpga_strm_0513",
        "build_perf_fpga_sw",
        [],
        repeat=1,
        tags=["Coyote"],
    )
    sched_perf_fpga_vfpio = benchmark(
        "sched_perf_fpga_vfpio",
        "cyt_top_perf_fpga_io_0511",
        "build_perf_fpga_sw",
        [],
        repeat=1,
        tags=["vFPIO"],
    )

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
        "gzip_coyote": gzip_coyote,
    }

    Exp_6_1_vfpio_list = {
        "aes_vfpio": aes_vfpio,
        "sha256_vfpio": sha256_vfpio,
        "md5_vfpio": md5_vfpio,
        "nw_vfpio": nw_vfpio,
        "matmul_vfpio": matmul_vfpio,
        "sha3_vfpio": sha3_vfpio,
        "rng_vfpio": rng_vfpio,
        "gzip_vfpio": gzip_vfpio,
    }

    Exp_6_1_host_rdma_list = {
        "rdma_aes_host": rdma_aes_host,
        # "rdma_sha256_host": rdma_sha256_host,
        # "md5_vfpio": md5_vfpio,
        # "nw_vfpio": nw_vfpio,
        # "matmul_vfpio": matmul_vfpio,
        # "sha3_vfpio": sha3_vfpio,
        # "rng_vfpio": rng_vfpio,
        # "gzip_vfpio": gzip_vfpio
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

    Exp_6_1_vfpio_rdma_list = {
        # "rdma_aes_vfpio": rdma_aes_vfpio,
        # "rdma_sha256_vfpio": rdma_sha256_vfpio,
        "rdma_md5_vfpio": rdma_md5_vfpio,
        "rdma_nw_vfpio": rdma_nw_vfpio,
        # "rdma_matmul_vfpio": rdma_matmul_vfpio,
        # "rdma_sha3_vfpio": rdma_sha3_vfpio,
        # "rdma_rng_vfpio": rdma_rng_vfpio,
        "rdma_gzip_vfpio": rdma_gzip_vfpio,
    }

    Exp_6_3_host_coyote_list = {
        "aes_host_coyote": aes_host_coyote,
        "sha256_host_coyote": sha256_host_coyote,
        "md5_host_coyote": md5_host_coyote,
        "nw_host_coyote": nw_host_coyote,
        "matmul_host_coyote": matmul_host_coyote,
        "sha3_host_coyote": sha3_host_coyote,
        "rng_host_coyote": rng_host_coyote,
        "gzip_host_coyote": gzip_host_coyote,
    }

    Exp_6_3_host_vfpio_list = {
        "aes_host_vfpio": aes_host_vfpio,
        "sha256_host_vfpio": sha256_host_vfpio,
        "md5_host_vfpio": md5_host_vfpio,
        "nw_host_vfpio": nw_host_vfpio,
        "matmul_host_vfpio": matmul_host_vfpio,
        "sha3_host_vfpio": sha3_host_vfpio,
        "rng_host_vfpio": rng_host_vfpio,
        "gzip_host_vfpio": gzip_host_vfpio,
    }

    Exp_6_3_pr_host_list = {
        "pr_part1_host": pr_part1_host,
        "pr_part2_host": pr_part2_host,
    }

    Exp_6_3_pr_hbm_list = {
        "pr_part1_hbm": pr_part1_hbm,
        "pr_part2_hbm": pr_part2_hbm,
    }

    Exp_6_3_vfpio_list = {
        "vfpio_switch": vfpio_switch,
    }

    Exp_6_4_1_cycle_list = {
        "sched_perf_host_coyote_cycle": sched_perf_host_coyote_cycle,
        "sched_perf_host_vfpio_cycle": sched_perf_host_vfpio_cycle,
    }

    Exp_6_4_1_cntx_list = {
        "sched_perf_host_coyote_cntx": sched_perf_host_coyote_cntx,
        "sched_perf_host_vfpio_cntx": sched_perf_host_vfpio_cntx,
    }

    Exp_6_4_2_host_list = {
        "sched_perf_host_coyote": sched_perf_host_coyote,
        "sched_perf_host_vfpio": sched_perf_host_vfpio,
    }

    Exp_6_4_2_fpga_list = {
        "sched_perf_fpga_coyote": sched_perf_fpga_coyote,
        "sched_perf_fpga_vfpio": sched_perf_fpga_vfpio,
    }

    Exp_6_5_resource_util = {}

    exp = args.experiments

    if exp == "simple":
        print("Running simple example.")
        for bench_name, bench_object in simple_list.items():
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            parse_6_1_output(output_result)

    elif exp == "Exp_6_1_host_list":
        print("Running Exp_6_1_host_list example.")
        for bench_name, bench_object in Exp_6_1_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_1_output(output_result)
            write_to_file("results_6_1.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_1_coyote_list":
        print("Running Exp_6_1_coyote_list example.")
        for bench_name, bench_object in Exp_6_1_coyote_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_1_output(output_result)
            write_to_file("results_6_1.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_1_vfpio_list":
        print("Running Exp_6_1_vfpio_list example.")
        for bench_name, bench_object in Exp_6_1_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_1_output(output_result)
            write_to_file("results_6_1.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_1_host_rdma_list":
        for bench_name, bench_object in Exp_6_1_host_rdma_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_rdma_benchmark(exp_res_path, bench_object, reprogram)
            parse_6_1_output(output_result)

    elif exp == "Exp_6_1_coyote_rdma_list":
        for bench_name, bench_object in Exp_6_1_coyote_rdma_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_rdma_benchmark(exp_res_path, bench_object, reprogram)
            parse_6_1_output(output_result)

    elif exp == "Exp_6_1_vfpio_rdma_list":
        for bench_name, bench_object in Exp_6_1_vfpio_rdma_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_rdma_benchmark(exp_res_path, bench_object, reprogram)
            parse_6_1_output(output_result)

    elif exp == "Exp_6_3_host_coyote_list":
        for bench_name, bench_object in Exp_6_3_host_coyote_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_3_output(output_result)
            write_to_file("results_6_3_host.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_3_host_vfpio_list":
        for bench_name, bench_object in Exp_6_3_host_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_3_output(output_result)
            write_to_file("results_6_3_host.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_3_pr_host_list":
        for bench_name, bench_object in Exp_6_3_pr_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_pr_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_3_pr_output(output_result)
            write_6_3_to_file(
                "results_6_3_pr.csv",
                output_data,
                bench_object.tags,
                bench_object.app_list,
            )

    elif exp == "Exp_6_3_pr_hbm_list":
        for bench_name, bench_object in Exp_6_3_pr_hbm_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_pr_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_3_pr_output(output_result)
            write_6_3_to_file(
                "results_6_3_pr.csv",
                output_data,
                bench_object.tags,
                bench_object.app_list,
            )

    elif exp == "Exp_6_3_vfpio_list":
        for bench_name, bench_object in Exp_6_3_vfpio_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            parse_6_3_vio_output(output_result)

    elif exp == "Exp_6_4_1_cycle_list":
        for bench_name, bench_object in Exp_6_4_1_cycle_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_4_1_output(output_result)
            write_6_4_1_to_file("results_6_4_cycle.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_4_1_cntx_list":
        for bench_name, bench_object in Exp_6_4_1_cntx_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_cntx_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_4_1_2_output(output_result)
            write_6_4_1_2_to_file(
                "results_6_4_cntx.csv", output_data, bench_object.tags
            )

    elif exp == "Exp_6_4_2_host_list":
        for bench_name, bench_object in Exp_6_4_2_host_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_cntx_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_4_2_host_output(output_result)
            write_6_4_2_to_file("results_6_4_host.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_4_2_fpga_list":
        for bench_name, bench_object in Exp_6_4_2_fpga_list.items():
            # print(bench_object.name)
            print("--------------------------------------------")
            output_result = run_benchmark(exp_res_path, bench_object, reprogram)
            output_data = parse_6_4_2_fpga_output(output_result)
            write_6_4_2_to_file("results_6_4_fpga.csv", output_data, bench_object.tags)

    elif exp == "Exp_6_5_resource_util":
        print("--------------------------------------------")
        extract_util("util_coyote.csv", "util_vfpio.csv")

    else:
        # for bench_name, bench_object in Exp_6_1_host_list.items():
        #     # print(bench_object.name)
        #     print("--------------------------------------------")
        #     run_benchmark(exp_res_path, bench_object, reprogram)

        # for bench_name, bench_object in Exp_6_4_2_vfpio_list.items():
        #     # print(bench_object.name)
        #     print("--------------------------------------------")
        #     run_pr_benchmark(exp_res_path, bench_object ,reprogram)
        print("No evaluation selected.")

    print("--------------------------------------------")
    print("exp result path: " + exp_res_path)

    # parse_output("LICENSE.md")
    print("Finished")


if __name__ == "__main__":
    # get timestamp
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%H_%M")
    exp_res_path = os.path.join(os.path.realpath("."), "exp-results")
    pathlib.Path(exp_res_path).mkdir(parents=True, exist_ok=True)

    log_filename = os.path.join(exp_res_path, "log_" + timestamp + ".log")
    logging.basicConfig(
        level=logging.DEBUG,
        filename=log_filename,
        filemode="a+",
        format="%(asctime)-15s %(levelname)-8s %(message)s",
    )
    main()
