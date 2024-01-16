//
// BASE RDMA operations
//

// Tie-off
always_comb axi_ctrl.tie_off_s();

// UL
`ifdef EN_RDMA_0

`META_ASSIGN(rdma_0_rd_req, bpss_rd_req)
`META_ASSIGN(rdma_0_wr_req, bpss_wr_req)

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

AXI4SR axis_rdma_0_sink2();

// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_rdma_0_sink2), .m_axis(axis_sink_int));
axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_host_0_src));

// // UL
// always_comb begin
//     axis_src_int.tvalid  = axis_sink_int.tvalid;
//     for(int i = 0; i < 16; i++)
//         axis_src_int.tdata[i*32+:32] = axis_sink_int.tdata[i*32+:32] + 1; 
//     axis_src_int.tkeep   = axis_sink_int.tkeep;
//     axis_src_int.tid     = axis_sink_int.tid;
//     axis_src_int.tlast   = axis_sink_int.tlast;
    
//     axis_sink_int.tready = axis_src_int.tready;
// end

localparam integer N_AES_PIPELINES = 4;

logic [127:0] key;
logic key_start;
logic key_done;

// Slave
aes_slave inst_slave (
    .aclk(aclk),
    .aresetn(aresetn),
    .axi_ctrl(axi_ctrl),
    .key_out(key),
    .keyStart(key_start)
);

// AES pipelines
aes_top #(
    .NPAR(N_AES_PIPELINES)
) inst_aes_top (
    .clk(aclk),
    .reset_n(aresetn),
    .stall(~axis_src_int.tready),
    .key_in(key),
    .keyVal_in(key_start),
    .keyVal_out(key_done),
    .last_in(axis_sink_int.tlast),
    .last_out(axis_src_int.tlast),
    .keep_in(axis_sink_int.tkeep),
    .keep_out(axis_src_int.tkeep),
    .dVal_in(axis_sink_int.tvalid),
    .dVal_out(axis_src_int.tvalid),
    .data_in(axis_sink_int.tdata),
    .data_out(axis_src_int.tdata)
);

assign axis_sink_int.tready = axis_src_int.tready;
assign axis_src_int.tid = 0;