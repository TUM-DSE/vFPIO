#!/usr/bin/env python3

import csv
import argparse


def average(lst):
    return round(sum(lst) / len(lst), 2)


def process_6_1(input_filename, output_filename):
    dic = {}
    dic_rdma = {}
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            if "rdma" not in row[1]:
                key = row[0]
                if key not in dic:
                    dic[key] = dict.fromkeys(["Host", "Coyote", "vFPIO"], [])
                    dic[key][row[1]] = list(map(float, row[2:]))
                else:
                    dic[key][row[1]] += list(map(float, row[2:]))
            else:
                tag = row[1].split("_")[1]
                key = " " + row[0] + " "
                if key not in dic_rdma:
                    dic_rdma[key] = dict.fromkeys(["Host", "Coyote", "vFPIO"], [])
                    dic_rdma[key][tag] = list(map(float, row[2:]))
                else:
                    dic_rdma[key][tag] += list(map(float, row[2:]))
    # print(dic)
    # print(dic_rdma)
    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["app", "throughput", "platform"])

        for key in dic:
            for platform in dic[key]:
                out = [key, average(dic[key][platform]), platform]
                csv_writer.writerow(out)

        for key in dic_rdma:
            for platform in dic_rdma[key]:
                out = [key, average(dic_rdma[key][platform]), platform]
                csv_writer.writerow(out)

    print("write finished")


def process_6_4_cycle(input_filename, output_filename):
    dic = {}
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            key = row[0]
            if not row:
                continue
            if key not in dic:
                dic[key] = list(map(float, row[1:]))
            else:
                dic[key] += list(map(float, row[1:]))

    print(dic)

    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["priority", "cycle"])
        for key in dic:
            out = [key, average(dic[key])]
            csv_writer.writerow(out)
    print("write finished")


def process_6_4_cntx(input_filename, output_filename):
    dic = {}
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            if not row:
                continue
            key = (row[0], row[2])
            if key not in dic:
                dic[key] = [float(row[1])]
            else:
                dic[key] += [float(row[1])]

    # print(dic)

    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["size", "count", "platform"])
        for key in dic:
            out = [key[0], average(dic[key]), key[1]]
            csv_writer.writerow(out)
    print("write finished")


def process_6_4(input_filename, output_filename):
    dic = {}
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            # print(row)
            if not row:
                continue
            key = (row[0], row[2])
            if key not in dic:
                dic[key] = [float(row[1])]
            else:
                dic[key] += [float(row[1])]

    # print(dic)

    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Size[KiB]", "Cycle", "Platform"])
        for key in dic:
            out = [key[0], average(dic[key]), key[1]]
            csv_writer.writerow(out)
    print("write finished")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiments",
        "-e",
        type=str,
        default="simple",
        help="select the experiments to run",
    )
    args = parser.parse_args()

    exp = args.experiments

    if exp == "6_1":
        input_file = "results_6_1.csv"
        output_file = "e2e.csv"
        print("Running 6_1 example.")
        process_6_1(input_file, output_file)
        print("exp result path: " + output_file)

    elif exp == "6_4_cycle":
        input_file = "results_6_4_cycle.csv"
        output_file = "performance_isolation.csv"
        print("Running 6_4_cycle example.")
        process_6_4_cycle(input_file, output_file)
        print("exp result path: " + output_file)

    elif exp == "6_4_cntx":
        input_file = "results_6_4_cntx.csv"
        output_file = "context_switch.csv"
        print("Running 6_4_cntx example.")
        process_6_4_cntx(input_file, output_file)
        print("exp result path: " + output_file)

    elif exp == "6_4_host":
        input_file = "results_6_4_host.csv"
        output_file = "performance_overhead_perf_host.csv"
        print("Running 6_4_host example.")
        process_6_4(input_file, output_file)
        print("exp result path: " + output_file)
    elif exp == "6_4_fpga":
        input_file = "results_6_4_fpga.csv"
        output_file = "performance_overhead_perf_fpga.csv"
        print("Running 6_4_fpga example.")
        process_6_4(input_file, output_file)
        print("exp result path: " + output_file)
    else:
        print("No evaluation selected.")

    print("--------------------------------------------")

    # parse_output("LICENSE.md")
    print("Finished")


if __name__ == "__main__":

    main()
