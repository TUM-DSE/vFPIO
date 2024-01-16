set axis_dwidth_converter_0 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_0]

set_property -dict { 
    CONFIG.S_TDATA_NUM_BYTES {64}
    CONFIG.M_TDATA_NUM_BYTES {4}
    CONFIG.HAS_TLAST {1}
    CONFIG.HAS_TKEEP {1}
} [get_ips axis_dwidth_converter_0]

set_property -dict { 
    GENERATE_SYNTH_CHECKPOINT {1}
} $axis_dwidth_converter_0