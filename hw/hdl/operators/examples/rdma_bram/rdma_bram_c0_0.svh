// I/O
AXI4SR axis_rdma_0_sink2();

// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_rdma_0_sink2), .m_axis(axis_sink_int));
axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_host_0_src));

// UL
`ifdef EN_RDMA_0

`META_ASSIGN(rdma_0_rd_req, bpss_rd_req)
`META_ASSIGN(bpss_tmp, bpss_wr_req)

`ifndef EN_MEM
// One 'axis_rdma_0_sink' line and one 'axis_host_0_sink' line should be uncommented
`AXISR_ASSIGN(axis_rdma_0_sink, axis_rdma_0_sink2) // RDMA => user logic => host
//`AXISR_ASSIGN(axis_rdma_0_sink, axis_host_0_src) // RDMA => host
// `AXISR_ASSIGN(axis_host_0_sink, axis_host_sink2)   // Host => user logic => RDMA
`AXISR_ASSIGN(axis_host_0_sink, axis_rdma_0_src) // Host => RDMA
`else
`AXISR_ASSIGN(axis_rdma_0_sink, axis_card_0_src)
`AXISR_ASSIGN(axis_card_0_sink, axis_rdma_0_src)
`endif

`else
`ifdef EN_RDMA_1

`META_ASSIGN(rdma_1_rd_req, bpss_rd_req)
`META_ASSIGN(rdma_1_wr_req, bpss_wr_req)

`ifndef EN_MEM
`AXISR_ASSIGN(axis_rdma_1_sink, axis_host_0_src)
`AXISR_ASSIGN(axis_host_0_sink, axis_rdma_1_src)
`else
`AXISR_ASSIGN(axis_rdma_1_sink, axis_card_0_src)
`AXISR_ASSIGN(axis_card_0_sink, axis_rdma_1_src)
`endif

`endif
`endif

`ifdef EN_RDMA_0
metaIntf #(.STYPE(req_t)) bpss_tmp();
assign bpss_tmp.valid                   = rdma_0_wr_req.valid;
assign rdma_0_wr_req.ready              = bpss_tmp.ready;

assign bpss_tmp.data.vaddr = rdma_0_wr_req.data.vaddr;
assign bpss_tmp.data.len = 64;
assign bpss_tmp.data.stream = rdma_0_wr_req.data.stream;
assign bpss_tmp.data.sync = rdma_0_wr_req.data.sync;
assign bpss_tmp.data.ctl = rdma_0_wr_req.data.ctl;
assign bpss_tmp.data.host = rdma_0_wr_req.data.host;
assign bpss_tmp.data.dest = rdma_0_wr_req.data.dest;
assign bpss_tmp.data.pid = rdma_0_wr_req.data.pid;
assign bpss_tmp.data.vfid = rdma_0_wr_req.data.vfid;
assign bpss_tmp.data.rsrvd = rdma_0_wr_req.data.rsrvd;
`endif


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


