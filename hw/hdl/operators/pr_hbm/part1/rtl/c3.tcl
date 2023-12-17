file mkdir $build_dir/iprepo
set cmd "exec unzip $hw_dir/hdl/operators/pr_hbm/part1/rtl/sha256_axis_fpga_*.zip -d $build_dir/iprepo/sha256_ip"
eval $cmd
update_ip_catalog -rebuild


for {set j 0}  {$j < $cfg(n_reg)} {incr j} {

	set sha256_axis_fpga_0 [create_ip -name sha256_axis_fpga -vendor dse.in.tum.de -library hls_sha -version 0.3 -module_name sha256_axis_fpga_c3_$j]

	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $sha256_axis_fpga_0

	move_files -of_objects [get_reconfig_modules design_user_wrapper_c3_$j] [get_files sha256_axis_fpga_c3_$j.xci]
	
}
