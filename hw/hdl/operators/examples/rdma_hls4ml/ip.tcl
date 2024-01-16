file mkdir $build_dir/iprepo
set cmd "exec unzip $hw_dir/hdl/operators/examples/rdma_hls4ml/dse_in_tum_de_hls4ml_myproject_*.zip -d $build_dir/iprepo/hls4ml_ip"
eval $cmd
update_ip_catalog -rebuild


	
set axis_dwidth_converter_c1 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_c1]

# User Parameters
set_property -dict [list \
    CONFIG.M_TDATA_NUM_BYTES {6} \
    CONFIG.S_TDATA_NUM_BYTES {64} \
] [get_ips axis_dwidth_converter_c1]

# Runtime Parameters
set_property -dict { 
    GENERATE_SYNTH_CHECKPOINT {1}
} $axis_dwidth_converter_c1

# move_files -of_objects [get_reconfig_modules design_user_wrapper_c5_$j] [get_files axis_dwidth_converter_c1.xci]


set hls4ml_0 [create_ip -name myproject -vendor dse.in.tum.de -library hls4ml -version 0.2 -module_name hls4ml_0]

set_property -dict { 
    GENERATE_SYNTH_CHECKPOINT {1}
} $hls4ml_0

		
