for {set j 0}  {$j < $cfg(n_reg)} {incr j} {

  set axi_bram_ctrl_0 [create_ip -name axi_bram_ctrl -vendor xilinx.com -library ip -version 4.1 -module_name axi_bram_ctrl_c3_$j]

  set_property -dict { 
    CONFIG.DATA_WIDTH {512}
    CONFIG.ID_WIDTH {16}
    CONFIG.PROTOCOL {AXI4}
    CONFIG.SUPPORTS_NARROW_BURST {1}
    CONFIG.SINGLE_PORT_BRAM {0}
    CONFIG.BMG_INSTANCE {INTERNAL}
    CONFIG.MEM_DEPTH {4096}
    CONFIG.RD_CMD_OPTIMIZATION {1}
  } [get_ips axi_bram_ctrl_c3_$j]

  set_property -dict { 
    GENERATE_SYNTH_CHECKPOINT {1}
  } $axi_bram_ctrl_0

	move_files -of_objects [get_reconfig_modules design_user_wrapper_c3_$j] [get_files axi_bram_ctrl_c3_$j.xci]
}