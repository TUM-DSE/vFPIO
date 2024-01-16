
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();


always_comb axi_ctrl.tie_off_s();

axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));


`ifdef EN_RDMA_0
metaIntf #(.STYPE(req_t)) bpss_tmp();
assign bpss_tmp.valid                   = rdma_0_wr_req.valid;
assign rdma_0_wr_req.ready              = bpss_tmp.ready;

assign bpss_tmp.data.vaddr = rdma_0_wr_req.data.vaddr;
assign bpss_tmp.data.len = 2047;
assign bpss_tmp.data.stream = rdma_0_wr_req.data.stream;
assign bpss_tmp.data.sync = rdma_0_wr_req.data.sync;
assign bpss_tmp.data.ctl = rdma_0_wr_req.data.ctl;
assign bpss_tmp.data.host = rdma_0_wr_req.data.host;
assign bpss_tmp.data.dest = rdma_0_wr_req.data.dest;
assign bpss_tmp.data.pid = rdma_0_wr_req.data.pid;
assign bpss_tmp.data.vfid = rdma_0_wr_req.data.vfid;
assign bpss_tmp.data.rsrvd = rdma_0_wr_req.data.rsrvd;
`endif


rng_axis_wrapper rng_inst (
    .aclk(aclk),
    .aresetn(aresetn),
    .axis_in(axis_sink_int),
    .axis_out(axis_src_int)
);
