#!/usr/bin/env python3

import csv
import argparse


def average(lst):
    return round(sum(lst) / len(lst), 2)


def percentage(a, b):
    if a == 0:
        return 0
    return round((a - b) / a * 100, 1)


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


def process_6_2(input_filename, output_filename):
    res = []
    app_list = ["host", "aes", "sha256", "md5", "nw", "matmul", "sha3", "rng", "gzip"]
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if not row:
                continue
            words = row[0].split()
            # print(words)
            if words[0] == "Total":
                res.append([words[5], words[6]])
    print(res)

    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        for i, app in enumerate(app_list):
            out = [
                app,
                res[2 * i][0],
                res[2 * i + 1][0],
                percentage(float(res[2 * i][0]), float(res[2 * i + 1][0])),
                res[2 * i][1],
                res[2 * i + 1][1],
                percentage(float(res[2 * i][1]), float(res[2 * i + 1][1])),
            ]

            csv_writer.writerow(out)

    print("write finished")

def process_6_3(input_filename, input_filename_2, output_filename):
    res = []
    dic_hbm = {}
    dic_strm = {}
    app_list = ["aes", "sha256", "md5", "nw", "matmul", "sha3", "rng", "gzip"]
    with open(input_filename, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if not row:
                continue
            app = row[0]
            if app not in app_list:
                continue
            if app not in dic_hbm:
                dic_hbm[app] = dict.fromkeys(["Host", "Coyote", "vFPIO"], [])
                dic_hbm[app][row[2]] = float(row[1])
            else:
                dic_hbm[app][row[2]] = float(row[1])

    # print(dic_hbm)

    with open(input_filename_2, "r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if not row:
                continue
            app = row[0]
            if app not in app_list:
                continue
            if app not in dic_strm:
                dic_strm[app] = dict.fromkeys(["Host", "Coyote", "vFPIO"], [])
                dic_strm[app][row[2]] = float(row[1])
            else:
                dic_strm[app][row[2]] = float(row[1])

    # print(dic_strm)

    for app in app_list:
        res.append([app, dic_hbm[app]["vFPIO"], round(dic_hbm[app]["vFPIO"] / dic_hbm[app]["Coyote"] * 100, 1), 
            dic_strm[app]["vFPIO"], round(dic_strm[app]["vFPIO"] / dic_strm[app]["Coyote"] * 100, 1)])

    with open(output_filename, "w") as file:
        csv_writer = csv.writer(file)
        for row in res:
            csv_writer.writerow(row)


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

    elif exp == "6_2":
        input_file = "results_6_2.csv"
        output_file = "complexity.csv"
        print("Running 6_2 example.")
        process_6_2(input_file, output_file)
        print("exp result path: " + output_file)

    elif exp == "6_3":
        input_file = "e2e.csv"
        input_file_2 = "results_6_3.csv"
        output_file = "reconfig.csv"
        output_file_2 = "results_6_3_strm.csv"
        print("Running 6_3 example.")
        process_6_1(input_file_2, output_file_2)
        process_6_3(input_file, output_file_2, output_file)
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
