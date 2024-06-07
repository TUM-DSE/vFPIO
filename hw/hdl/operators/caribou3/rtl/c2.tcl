file mkdir $build_dir/iprepo
set cmd "exec unzip $hw_dir/hdl/operators/caribou3/rtl/harris_corner_*.zip -d $build_dir/iprepo/harris_corner_ip"
eval $cmd
update_ip_catalog -rebuild


for {set j 0}  {$j < $cfg(n_reg)} {incr j} {

	set cornerHarris_accel_0 [create_ip -name cornerHarris_accel -vendor user -library harriscorner -version 0.4 -module_name cornerHarris_accel_c2_$j]

	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $cornerHarris_accel_0

	move_files -of_objects [get_reconfig_modules design_user_wrapper_c2_$j] [get_files cornerHarris_accel_c2_$j.xci]
	
}