//
// BASE RDMA operations
//

// Tie-off
always_comb axi_ctrl.tie_off_s();

// UL
// `ifdef EN_RDMA_0

// `META_ASSIGN(rdma_0_rd_req, bpss_rd_req)
// `META_ASSIGN(rdma_0_wr_req, bpss_wr_req)

// `ifndef EN_MEM
// // One 'axis_rdma_0_sink' line and one 'axis_host_0_sink' line should be uncommented
// `AXISR_ASSIGN(axis_rdma_0_sink, axis_rdma_0_sink2) // RDMA => user logic => host
// //`AXISR_ASSIGN(axis_rdma_0_sink, axis_host_0_src) // RDMA => host
// // `AXISR_ASSIGN(axis_host_0_sink, axis_host_sink2)   // Host => user logic => RDMA
// `AXISR_ASSIGN(axis_host_0_sink, axis_rdma_0_src) // Host => RDMA
// `else
// `AXISR_ASSIGN(axis_rdma_0_sink, axis_card_0_src)
// `AXISR_ASSIGN(axis_card_0_sink, axis_rdma_0_src)
// `endif

// `else
// `ifdef EN_RDMA_1

// `META_ASSIGN(rdma_1_rd_req, bpss_rd_req)
// `META_ASSIGN(rdma_1_wr_req, bpss_wr_req)

// `ifndef EN_MEM
// `AXISR_ASSIGN(axis_rdma_1_sink, axis_host_0_src)
// `AXISR_ASSIGN(axis_host_0_sink, axis_rdma_1_src)
// `else
// `AXISR_ASSIGN(axis_rdma_1_sink, axis_card_0_src)
// `AXISR_ASSIGN(axis_card_0_sink, axis_rdma_1_src)
// `endif

// `endif
// `endif

// AXI4SR axis_rdma_0_sink2();

// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));


// UL
always_comb begin
    axis_src_int.tvalid  = axis_sink_int.tvalid;
    for(int i = 0; i < 16; i++)
        axis_src_int.tdata[i*32+:32] = axis_sink_int.tdata[i*32+:32] + 1; 
    axis_src_int.tkeep   = axis_sink_int.tkeep;
    axis_src_int.tid     = axis_sink_int.tid;
    axis_src_int.tlast   = axis_sink_int.tlast;
    
    axis_sink_int.tready = axis_src_int.tready;
end