# Reproduce paper results

The first step is to get the source code for vFPIO and change to the evaluation branch
```
git clone git@github.com:TUM-DSE/vFPIO.git vFPIO
cd vFPIO
git checkout vfpio
```

## For ATC evaluation testers

Due its special hardware requirments we provide ssh access to our evaluation machines. Please contact the paper author email address to obtain ssh keys. The machines will have the correct hardware and also software installed to run the experiments. 


Once your account has been established, you can use the following command to access our servers:

```
SSH_AUTH_SOCK= ssh -v -F /dev/null -i <path/to/privkey> -oProxyCommand="ssh tunnel@login.dos.cit.tum.de -i <path/to/privkey> -W %h:%p" <yourusername>@{server_name}.dos.cit.tum.de
- replace the {server_name} with the server name
- replace the <yourusername> with reviewer_username
- replace the <path/to/privkey> with the path to your private key file
```

If you run into problems you can write an email or join channel #vfpio on freenode for live chat (https://webchat.freenode.net/) for further questions.


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
# requires nix-shell vfpio.nix
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


Use the `reproduce.py` file to run the experiments. 

```
# requires nix-shell vfpio.nix
python3 reproduce.py -r -e Exp_6_1_host_list 
python3 reproduce.py -r -e Exp_6_1_coyote_list 
python3 reproduce.py -r -e Exp_6_1_vfpio_list 
python3 reproduce.py -r -e Exp_6_1_host_rdma_list 
python3 reproduce.py -r -e Exp_6_1_coyote_rdma_list 
python3 reproduce.py -r -e Exp_6_1_vfpio_rdma_list 
```

These will generate several csv files with recorded data. The `write_csv.py` processes these data and output a csv file for plotting script. Run the following to create the figure (`e2e.png`) for 6.1 .

```
python3 write_csv.py -e 6_1
python3 plot_e2e.py
```
#### 6.2 Programmability

Run the following command

```
# requires nix-shell vfpio.nix
# in the project repo root 
bash ./measure_complexity.sh > results_6_2.csv
python3 write_csv.py -e 6_2
```
This will generate a file `complexity.csv` that has all the data needed to fill Table 5. 

#### 6.3 Portability

The data for the vFPIO throughput in Table 5 is taken from the previous experiments. Run the following command to generate the reconfiguration time data:
```
python3 reproduce.py -r -e Exp_6_3_pr_host_list 
python3 reproduce.py -r -e Exp_6_3_pr_hbm_list 
python3 reproduce.py -r -e Exp_6_3_host_coyote_list
python3 reproduce.py -r -e Exp_6_3_host_vfpio_list
python3 reproduce.py -r -e Exp_6_3_vfpio_list
```

Two files will be generated, `results_6_3_host.csv` and `results_6_3_pr.csv`. 

```
python3 write_csv.py -e 6_3
```
This commands generates `reconfig.csv` which has the data to fill Table 5.


#### 6.4 Scheduler

Run the following command to obtain data for Figure 6 and 7. 
```
python3 reproduce.py -r -e Exp_6_4_1_cycle_list 
python3 reproduce.py -r -e Exp_6_4_1_cntx_list 
python3 reproduce.py -r -e Exp_6_4_2_host_list 
python3 reproduce.py -r -e Exp_6_4_2_fpga_list 
```

These commands will generate a set of csv files storing the experiments' results: `results_6_4_cntx.csv`, `results_6_4_cycle.csv`, `results_6_4_host.csv`, `results_6_4_fpga.csv`.

To plot the Figure 6 and 7, 

```
python3 write_csv.py -e 6_4_cycle
python3 write_csv.py -e 6_4_cntx

python3 plot_iso.py
```
This will generate figure `perf_sched.png` (Figure 6).


```
python3 write_csv.py -e 6_4_host
python3 write_csv.py -e 6_4_fpga

python3 plot_overhead.py
```

The plotting command will generate figure `perf_overhead.png` (Figure 7).


#### 6.5 Resource Overheads

To save compilation time, we provide shell resource utilization report with `util_coyote.csv` and `util_vfpio.csv`. These are generated by Xilinx's `Vivado`. Run the next command to extract resource utilization of each component:

```
# in project root dir (vFPIO/)
# requires nix-shell vfpio.nix
python3 reproduce.py -e Exp_6_5_resource_util
```




## Potential issues

### Program stuck or reports errors
The `reproduce.py` will generate log file (log with timestamp, e.g., `log_05_24_13_55.log`) and program specific output in `exp-results` folder. You can see what went wrong by checking the log files.



### Driver issue
Something wrong may happen when loading or unloading the driver. In that case, the easiest solution is to reboot. 


### No files in home directory after reboot
Sometimes after reboot, there will only be system folders and no user files. Keep rebooting and it will get fixed eventually. 


### Terminal cursor disappear after reproduce.py had an issue

This will happen when the script does not exit normally. Type `reset` to solve the issue.


<!-- ### Require IP 'll_compress_2'


Replace `username` with your username, such as `atcRev1`. Then to ssh into the server:

```
ssh username@amy.dos.cit.tum.de
ssh username@clara.dos.cit.tum.de
```


```
Host amy
     HostName amy.dos.cit.tum.de
     User username
     ForwardAgent yes
     ProxyJump tunnel
     
Host clara
     HostName clara.dos.cit.tum.de
     User username
     ForwardAgent yes
     ProxyJump tunnel
```


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


Run the following command to set the number of huge pages in the kernel. Otherwise the host application will be killed.

```
sudo sysctl -w vm.nr_hugepages=1024
```



Compile two repositories with Coyote and vFPIO.

For Coyote
```
# requires xilinx-shell
git checkout coyote-comp
mkdir build_io_coyote_hw && cd build_io_coyote_hw
cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=io_switch_ndp
make shell && make compile
```

For vFPIO

```
# requires xilinx-shell
git checkout vFPIO
mkdir build_io_vfpio_hw && cd build_io_vfpio_hw
cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=io_switch_ndp
make shell && make compile
```
To extract the two resource utilization files, run the following scripts (make sure you are not in `xilinx-shell`)

```
bash ./extract_csv.sh coyote
bash ./extract_csv.sh vfpio
```



-->

