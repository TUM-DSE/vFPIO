# Reproduce paper results

The first step is to get the source code for vFPIO and change to the evaluation branch
```
git clone git@github.com:TUM-DSE/vFPIO.git vFPIO
cd vFPIO
git checkout vfpio
```

## For ATC evaluation testers

Due its special hardware requirments we provide ssh access to our evaluation machines. Please contact the paper author email address to obtain ssh keys. The machines will have the correct hardware and also software installed to run the experiments. If you run into problems you can write an email or join channel #vfpio on freenode for live chat (https://webchat.freenode.net/) for further questions.

## Specs

### Software
- Operating system: Linux 6.8.9 NixOS 23.11
- [Nix](https://nixos.org/download.html): For reproducibility we use the nix package manager to download all build dependencies. We use `xilinx-shell` and `vfpio.nix` to provide a consistant runtime environment. 

- Python 3.11 or newer for the script that reproduces the evaluation


### Hardware
- AMD EPYC 7413 CPU x2
- Xilinx Alveo U280 FPGA x2
- 100GB/s network interface
- Host machine (Amy) is the main server while a second machine (Clara) is used for acting as the client during RDMA experiments.


## Getting Started Instructions

Here are the instructions to run a "Hello world"-like example, which is MD5 in our case. The software is located in the following Github repo: https://github.com/TUM-DSE/vFPIO.

### Building FPGA kernel driver


To build the driver, run the following command in the project root folder

```
nix-shell vfpio.nix
cd driver
make -C $(nix-build -E '(import <nixpkgs> {}).linuxPackages_6_8.kernel.dev' --no-out-link)/lib/modules/*/build M=$(pwd)
```


### Obtaining FPGA bitstream

FPGA bitstreams are used to program the FPGA with specified applications. Compiling a bistream for our FPGA takes a long time (3-4 hours). To save time, we provided pre-compiled bitstrems in `bitstreams` folder. 

Please do not change the position and the name of the bitstream folder.


### Compiling MD5 software

Run the following command to build the `io_app` software binary for running the MD5 host application with the vFPIO shell using FPGA memory.

```
nix-shell vfpio.nix
# in the project repo root 
mkdir build_io_app_sw && cd build_io_app_sw
cmake ../sw/ -DTARGET_DIR=examples/io_app
make
```


Set up hugepages for host application.

```
sudo sysctl -w vm.nr_hugepages=1024
```

### Running test example

Due to the long time requried for compiling FPGA bitstreams (3-4 hours), we suggest using our provided bitstream for evaluation.


Then run the experiments
```
# in the project repo root
python3 reproduce.py -r -e simple 
```

This command will run the MD5 host application 10 times and calculate the average throughput.



## Detailed Instructions

### Compilation

#### Software

In the project repo, run the following command to build all host applications

```
nix-shell vfpio.nix
# in the project repo root 
bash compile_sw.sh
```

Or to compile specific example, identify the application you want to build from `sw/examples/`, e.g. `io_app`, then run the following commands 
```
nix-shell vfpio.nix
# in the project repo root 
mkdir build_io_app_sw && cd build_io_app_sw
cmake ../sw/ -DTARGET_DIR=examples/io_app
make
```

### Hardware

Identify the hardware examples in `hw/hdl/operators/examples/`, e.g. `md5`, then run the following commands

```
xilinx-shell
mkdir build_md5_io_hw && cd build_md5_io_hw
cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=md5
make shell && make compile
```

This will take 3-4 hours to complete. To save time, you can 


### Running experiments


#### 6.1 Performance

Run the following command to set the number of huge pages in the kernel. Otherwise the host application will be killed.

```
sudo sysctl -w vm.nr_hugepages=1024
```

Use the `reproduce.py` file to run the experiments. 

```
python3 reproduce.py -r -e Exp_6_1_host_list 
python3 reproduce.py -r -e Exp_6_1_coyote_list 
python3 reproduce.py -r -e Exp_6_1_vfpio_list 
python3 reproduce.py -r -e Exp_6_1_host_rdma_list 
python3 reproduce.py -r -e Exp_6_1_coyote_rdma_list 
python3 reproduce.py -r -e Exp_6_1_vfpio_rdma_list 
```
These will generate several csv files with recorded data. Run the following to create the figure for 6.1.

```
python3 plot_e2e.py
```
#### 6.2 Programmability

Run the following command

```
nix-shell vfpio.nix
# in the project repo root 
bash ./measure_complexity.sh
```


#### 6.3 Portability

The data for the vFPIO throughput in Table 5 is taken from the previous experiments. Run the following command to generate the reconfiguration time data:
```
python3 reproduce.py -r -e Exp_6_3_host_list 
python3 reproduce.py -r -e Exp_6_3_hbm_list 
python3 reproduce.py -r -e Exp_6_3_vfpio_list
```


#### 6.4 Scheduler

Run the following command to obtain data for Figure 6 and 7. 
```
python3 reproduce.py -r -e Exp_6_4_1_cycles_list 
python3 reproduce.py -r -e Exp_6_4_1_cntx_list 
python3 reproduce.py -r -e Exp_6_4_2_host_list 
python3 reproduce.py -r -e Exp_6_4_2_fpga_list 
```


#### 6.5 Resource Overheads

Compile two repositories with Coyote and vFPIO.

For Coyote
```
# requires xilinx-shell
git checkout coyote-comp
mkdir build_io_coyote_hw && cd build_io_coyote_hw
cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=io_switch_ndp
make && make compile
```

For vFPIO

```
# requires xilinx-shell
git checkout vFPIO
mkdir build_io_vfpio_hw && cd build_io_vfpio_hw
cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=io_switch_ndp
make && make compile
```
To extract the two resource utilization files, run the following scripts

```
bash ./extract_csv.sh
```

This will generate two files: `util_coyote.csv` and `util_vfpio.csv`. Do not change the filenames, and run the next command to extract resource utilization of each component:

```
# in project root dir (vFPIO/)
python3 reproduce -e Exp_6_5_resource_util
```




## Potential issues

### Driver issue
Something wrong may happen when loading or unloading the driver. In that case, the easiest solution is to reboot. 


### No files in home directory after reboot
Sometimes after reboot, there will only be system folders and no user files. Keep rebooting and it will get fixed eventually. 


### Terminal cursor disappear after reproduce.py had an issue

This will happen when the script does not exit normally. Type `reset` to solve the issue.


<!-- ### Require IP 'll_compress_2'
 -->



<!--  
```
bash ./extract_csv.sh
```
```
open_project build_io_hw/lynx/lynx.xpr
open_run impl_1
report_utilization -name util_1 -spreadsheet_file util_coyote_io.xlsx
report_utilization -hierarchical  -file util_vfpio_test.csv
ssconvert util_vfpio.xlsx util_vfpio.csv
```
cmake ../hw/ -DFDEV_NAME=u50 -DEXAMPLE=caribou -DN_REGIONS=2 -DN_CONFIG=10 -DUCLK_F=250 -DACLK_F=250 -DCOMP_CORES=24

-->
