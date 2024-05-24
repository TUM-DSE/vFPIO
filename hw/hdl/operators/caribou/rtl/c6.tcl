for {set j 0}  {$j < $cfg(n_reg)} {incr j} {

	set blk_mem_gen_0 [create_ip -name blk_mem_gen -vendor xilinx.com -library ip -version 8.4 -module_name blk_mem_gen_c6_$j]

	set_property -dict {
	  CONFIG.Use_Byte_Write_Enable {true}
	  CONFIG.Byte_Size {8}
	  CONFIG.Algorithm {Minimum_Area}
	  CONFIG.Primitive {8kx2}
	  CONFIG.Write_Width_A {4096}
	  CONFIG.Write_Depth_A {64}
	  CONFIG.Read_Width_A {4096}
	  CONFIG.Enable_A {Always_Enabled}
	  CONFIG.Write_Width_B {4096}
	  CONFIG.Read_Width_B {4096}
	  CONFIG.Register_PortA_Output_of_Memory_Primitives {false}
	  CONFIG.Fill_Remaining_Memory_Locations {false}
	  CONFIG.Use_RSTA_Pin {false}
	  CONFIG.EN_SAFETY_CKT {false}
	} [get_ips blk_mem_gen_c6_$j]

	set_property -dict {
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $blk_mem_gen_0
		       
	move_files -of_objects [get_reconfig_modules design_user_wrapper_c6_$j] [get_files blk_mem_gen_c6_$j.xci]
	
}
