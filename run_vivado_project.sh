# bash script to invoke the tcl script that extract resource utilization 
vivado -mode tcl -source ./extract_util.tcl -tclargs $1