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

metaIntf #(.STYPE(req_t)) bpss_tmp();
assign bpss_tmp.valid                   = rdma_0_wr_req.valid;
assign rdma_0_wr_req.ready              = bpss_tmp.ready;

assign bpss_tmp.data.vaddr = rdma_0_wr_req.data.vaddr;
assign bpss_tmp.data.len = rdma_0_wr_req.data.len / 2;
assign bpss_tmp.data.stream = rdma_0_wr_req.data.stream;
assign bpss_tmp.data.sync = rdma_0_wr_req.data.sync;
assign bpss_tmp.data.ctl = rdma_0_wr_req.data.ctl;
assign bpss_tmp.data.host = rdma_0_wr_req.data.host;
assign bpss_tmp.data.dest = rdma_0_wr_req.data.dest;
assign bpss_tmp.data.pid = rdma_0_wr_req.data.pid;
assign bpss_tmp.data.vfid = rdma_0_wr_req.data.vfid;
assign bpss_tmp.data.rsrvd = rdma_0_wr_req.data.rsrvd;

matmul_ab matmul_inst (
    .aclk(aclk),
    .aresetn(aresetn),

    .axis_in(axis_sink_int),
    .axis_out(axis_src_int)
    );