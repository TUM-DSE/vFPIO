// Tie-off
always_comb axi_ctrl.tie_off_s();
// always_comb axis_card_0_src.tie_off_m();
// always_comb axis_host_0_sink.tie_off_s();

// I/O
// AXI4SR axis_sink_int ();
// AXI4SR axis_src_int ();

// axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
// axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));
// axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_card_0_sink), .m_axis(axis_sink_int));
// axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_card_0_src));

`ifdef EN_VIO // vFPIO only
axisr_reg inst_reg_direct (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_switch_mem_0_src));
`else // Coyote
`AXISR_ASSIGN(axis_card_0_sink, axis_card_0_src)
`AXISR_ASSIGN(axis_host_0_sink, axis_host_0_src)

`AXISR_ASSIGN(axis_rdma_0_sink, axis_rdma_0_src)
`AXISR_ASSIGN(axis_rdma_1_sink, axis_rdma_1_src)
`endif

// UL
// always_comb begin
//     axis_src_int.tvalid  = axis_sink_int.tvalid;
//     axis_src_int.tdata   = axis_sink_int.tdata;
//     axis_src_int.tkeep   = axis_sink_int.tkeep;
//     axis_src_int.tid     = axis_sink_int.tid;
//     axis_src_int.tlast   = axis_sink_int.tlast;
//     axis_sink_int.tready = axis_src_int.tready;
// end
