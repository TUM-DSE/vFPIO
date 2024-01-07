file mkdir $build_dir/iprepo
set cmd "exec unzip $hw_dir/hdl/operators/examples/sha256hls/sha256_axis_fpga_0.zip -d $build_dir/iprepo/sha256_ip"
eval $cmd
update_ip_catalog -rebuild


set sha256_axis_fpga_0 [create_ip -name sha256_axis_fpga -vendor dse.in.tum.de -library hls_sha -version 0.3 -module_name sha256_axis_fpga_0]

set_property -dict { 
    GENERATE_SYNTH_CHECKPOINT {1}
} $sha256_axis_fpga_0

	
