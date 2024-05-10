// I/O
AXI4SR axis_in ();
AXI4SR axis_out ();

always_comb axi_ctrl.tie_off_s();

axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_in));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_out), .m_axis(axis_switch_mem_0_src));

matmul_ab matmul_inst (
    .aclk(aclk),
    .aresetn(aresetn),
    
    .axis_in(axis_in),
    .axis_out(axis_out)
    );