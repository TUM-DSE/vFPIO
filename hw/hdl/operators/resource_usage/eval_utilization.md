First, build the Coyote shell: 
```
source /share/xilinx/Vivado/2022.1/settings64.sh
cd <root of coyote repo>
mkdir build_resource_usage && cd build_resource_usage
/bin/cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=resource_usage
nohup make shell &
nohup make compile &
vivado lynx/lynx.xpr &
```

Then, open implementation in Vivado GUI, and execute the following command in Tcl terminal:
```
report_utilization -name util_1 -spreadsheet_file util_coyote.xlsx
```



