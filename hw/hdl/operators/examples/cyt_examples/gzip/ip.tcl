

	set clk_wiz_0 [create_ip -name clk_wiz -vendor xilinx.com -library ip -version 6.0 -module_name clk_wiz_0]

	# User Parameters
	set_property -dict [list \
	  CONFIG.AUTO_PRIMITIVE {BUFGCE_DIV} \
	  CONFIG.CLKIN1_JITTER_PS {40.0} \
	  CONFIG.CLKOUT1_DRIVES {Buffer} \
	  CONFIG.CLKOUT1_JITTER {85.736} \
	  CONFIG.CLKOUT1_PHASE_ERROR {79.008} \
	  CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {250} \
	  CONFIG.CLKOUT2_DRIVES {Buffer} \
	  CONFIG.CLKOUT2_JITTER {98.122} \
	  CONFIG.CLKOUT2_PHASE_ERROR {79.008} \
	  CONFIG.CLKOUT2_REQUESTED_OUT_FREQ {125} \
	  CONFIG.CLKOUT2_USED {true} \
	  CONFIG.CLKOUT3_DRIVES {Buffer} \
	  CONFIG.CLKOUT4_DRIVES {Buffer} \
	  CONFIG.CLKOUT5_DRIVES {Buffer} \
	  CONFIG.CLKOUT6_DRIVES {Buffer} \
	  CONFIG.CLKOUT7_DRIVES {Buffer} \
	  CONFIG.FEEDBACK_SOURCE {FDBK_AUTO} \
	  CONFIG.MMCM_BANDWIDTH {OPTIMIZED} \
	  CONFIG.MMCM_CLKFBOUT_MULT_F {5.000} \
	  CONFIG.MMCM_CLKIN1_PERIOD {4.000} \
	  CONFIG.MMCM_CLKIN2_PERIOD {10.0} \
	  CONFIG.MMCM_CLKOUT0_DIVIDE_F {5.000} \
	  CONFIG.MMCM_CLKOUT1_DIVIDE {10} \
	  CONFIG.MMCM_COMPENSATION {AUTO} \
	  CONFIG.MMCM_DIVCLK_DIVIDE {1} \
	  CONFIG.NUM_OUT_CLKS {2} \
	  CONFIG.OPTIMIZE_CLOCKING_STRUCTURE_EN {true} \
	  CONFIG.PRIMITIVE {Auto} \
	  CONFIG.PRIM_IN_FREQ {250} \
	  CONFIG.PRIM_SOURCE {Global_buffer} \
	  CONFIG.USE_LOCKED {false} \
	  CONFIG.USE_RESET {false} \
	] [get_ips clk_wiz_0]

	# Runtime Parameters
	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $clk_wiz_0


	set axis_clock_converter_2 [create_ip -name axis_clock_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_clock_converter_2]

	# User Parameters
	set_property -dict [list \
	  CONFIG.HAS_TKEEP {1} \
	  CONFIG.HAS_TLAST {1} \
	  CONFIG.TDATA_NUM_BYTES {32} \
	] [get_ips axis_clock_converter_2]

	# Runtime Parameters
	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $axis_clock_converter_2


	set axis_dwidth_converter_in_2 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_in_2]

	# User Parameters
	set_property -dict [list \
	  CONFIG.HAS_MI_TKEEP {0} \
	  CONFIG.HAS_TKEEP {1} \
	  CONFIG.HAS_TLAST {1} \
	  CONFIG.M_TDATA_NUM_BYTES {32} \
	  CONFIG.S_TDATA_NUM_BYTES {64} \
	] [get_ips axis_dwidth_converter_in_2]

	# Runtime Parameters
	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $axis_dwidth_converter_in_2



	set axis_dwidth_converter_out_2 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_out_2]

	# User Parameters
	set_property -dict [list \
	  CONFIG.HAS_MI_TKEEP {1} \
	  CONFIG.HAS_TKEEP {1} \
	  CONFIG.HAS_TLAST {1} \
	  CONFIG.M_TDATA_NUM_BYTES {64} \
	  CONFIG.S_TDATA_NUM_BYTES {32} \
	] [get_ips axis_dwidth_converter_out_2]

	# Runtime Parameters
	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $axis_dwidth_converter_out_2


	set ll_compress_2 [create_ip -name ll_compress -vendor xilinx.com -library ip -version 2.1 -module_name ll_compress_2]

	# User Parameters
	set_property -dict [list \
	  CONFIG.COMP_EN_OUTPUT_FIFO {true} \
	  CONFIG.COMP_MODE {Compression} \
	  CONFIG.DIN_WIDTH {256} \
	  CONFIG.RFC_TYPE {GZIP} \
	] [get_ips ll_compress_2]

	# Runtime Parameters
	set_property -dict { 
	  GENERATE_SYNTH_CHECKPOINT {1}
	} $ll_compress_2


