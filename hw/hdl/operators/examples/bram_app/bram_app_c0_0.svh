
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();


always_comb axi_ctrl.tie_off_s();

axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));

wire [15:0] rd_addr = axis_sink_int.tdata[0+:16];

read_only_axi_ram ro_ram(
    .clk(aclk),
    .rst(aresetn),
    .s_axi_arid(axis_sink_int.tid),
    .s_axi_araddr(rd_addr),
    .s_axi_arvalid(axis_sink_int.tvalid),
    .s_axi_arready(axis_sink_int.tready),
    .s_axi_rid(axis_src_int.tid),
    .s_axi_rdata(axis_src_int.tdata),
    .s_axi_rlast(axis_src_int.tlast),
    .s_axi_rvalid(axis_src_int.tvalid),
    .s_axi_rready(axis_src_int.tready)
    );