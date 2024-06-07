file mkdir $build_dir/iprepo
set cmd "exec unzip $hw_dir/hdl/operators/caribou/rtl/hyperloglog_*.zip -d $build_dir/iprepo/hyperloglog_ip"
eval $cmd
update_ip_catalog -rebuild


for {set j 0}  {$j < $cfg(n_reg)} {incr j} {
	
	set design_user_hls_0 [create_ip -name design_user_hls_c0_0 -vendor user -library hyperloglog -version 0.1 -module_name hyperloglog_c8_$j]

	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $design_user_hls_0

	move_files -of_objects [get_reconfig_modules design_user_wrapper_c8_$j] [get_files hyperloglog_c8_$j.xci]
		
}
