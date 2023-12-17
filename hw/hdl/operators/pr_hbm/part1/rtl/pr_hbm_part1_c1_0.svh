// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

always_comb axi_ctrl.tie_off_s();

`ifdef EN_VIO // vFPIO only
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));
`else
`ifdef EN_STRM
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_host_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_host_0_src));
`elsif EN_MEM
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_card_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_card_0_src));
`endif
`endif // EN_VIO

// UL
nw_axis_wrapper nw_inst (
    .aclk(aclk),
    .aresetn(aresetn),
    .axis_in(axis_sink_int),
    .axis_out(axis_src_int)
);
