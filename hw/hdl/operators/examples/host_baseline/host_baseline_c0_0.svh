// Tie-off
always_comb axi_ctrl.tie_off_s();
// always_comb axis_card_0_src.tie_off_m();
// always_comb axis_host_0_sink.tie_off_s();

// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

`ifdef EN_STRM
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_host_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_host_0_src));
`else
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_card_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_card_0_src));
`endif

always_comb begin
    axis_src_int.tvalid  = axis_sink_int.tvalid;
    axis_src_int.tdata = ~axis_sink_int.tdata;
    axis_src_int.tkeep   = axis_sink_int.tkeep;
    axis_src_int.tid     = axis_sink_int.tid;
    axis_src_int.tlast   = axis_sink_int.tlast;
    axis_sink_int.tready = axis_src_int.tready;
end