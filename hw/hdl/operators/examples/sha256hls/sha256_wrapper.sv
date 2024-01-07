module sha256_wrapper (
    input aclk,
    input aresetn,
    
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
    );

reg ap_start = 0;
logic ap_done;
logic ap_idle;
logic ap_ready;

sha256_axis_fpga_0 sha256_inst (
  .ap_clk(aclk),                                        // input wire ap_clk
  .ap_rst_n(aresetn),                                    // input wire ap_rst_n
  .ap_start(ap_start),                                    // input wire ap_start
  .ap_done(ap_done),                                      // output wire ap_done
  .ap_idle(ap_idle),                                      // output wire ap_idle
  .ap_ready(ap_ready),                                    // output wire ap_ready
  .s_axis_host_0_sink_TVALID(axis_in.tvalid),  // input wire s_axis_host_0_sink_TVALID
  .s_axis_host_0_sink_TREADY(axis_in.tready),  // output wire s_axis_host_0_sink_TREADY
  .s_axis_host_0_sink_TDATA(axis_in.tdata),    // input wire [511 : 0] s_axis_host_0_sink_TDATA
  .s_axis_host_0_sink_TID(6'b0),        // input wire [5 : 0] s_axis_host_0_sink_TID
  .s_axis_host_0_sink_TKEEP(axis_in.tkeep),    // input wire [63 : 0] s_axis_host_0_sink_TKEEP
  .s_axis_host_0_sink_TSTRB(64'b1),    // input wire [63 : 0] s_axis_host_0_sink_TSTRB
  .s_axis_host_0_sink_TLAST(axis_in.tlast),    // input wire [0 : 0] s_axis_host_0_sink_TLAST
  .m_axis_host_0_src_TVALID(axis_out.tvalid),    // output wire m_axis_host_0_src_TVALID
  .m_axis_host_0_src_TREADY(axis_out.tready),    // input wire m_axis_host_0_src_TREADY
  .m_axis_host_0_src_TDATA(axis_out.tdata),      // output wire [511 : 0] m_axis_host_0_src_TDATA
  .m_axis_host_0_src_TID(axis_out.tid),          // output wire [5 : 0] m_axis_host_0_src_TID
  .m_axis_host_0_src_TKEEP(axis_out.tkeep),      // output wire [63 : 0] m_axis_host_0_src_TKEEP
  //.m_axis_host_0_src_TSTRB(m_axis_host_0_src_TSTRB),      // output wire [63 : 0] m_axis_host_0_src_TSTRB
  .m_axis_host_0_src_TLAST(axis_out.tlast)      // output wire [0 : 0] m_axis_host_0_src_TLAST
);

always_ff @(posedge aclk) begin
    if(ap_idle) begin
        ap_start <= 1;
    end
    if(ap_ready)
        ap_start <= 0;
end

endmodule
