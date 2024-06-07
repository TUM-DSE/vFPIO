`timescale 1ns / 1ps

module harris_corner_detection (
    input aclk,
    input aresetn,
    
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
);

reg ul_resetn = 0;

reg ap_start = 0;
logic ap_done;
logic ap_ready;
logic ap_idle;

assign axis_out.tid = 0;

always_ff @(posedge aclk) begin
    ul_resetn <= aresetn;
    if(ap_idle) begin
        ap_start <= 1;
    end
    if(ap_ready)
        ap_start <= 0;
end

cornerHarris_accel_c0_1 hcd_inst (
  .ap_clk(aclk),                                  // input wire ap_clk
  .ap_rst_n(ul_resetn),                           // input wire ap_rst_n
  .ap_start(ap_start),                            // input wire ap_start
  .ap_done(ap_done),                              // output wire ap_done
  .ap_ready(ap_ready),                            // output wire ap_ready
  .ap_idle(ap_idle),                              // output wire ap_idle
  .img_in_TVALID(axis_in.tvalid),                  // input wire img_in_TVALID
  .img_in_TREADY(axis_in.tready),                  // output wire img_in_TREADY
  .img_in_TDATA(axis_in.tdata),                    // input wire [511 : 0] img_in_TDATA
  .img_in_TKEEP(axis_in.tkeep),                    // input wire [63 : 0] img_in_TKEEP
  .img_in_TSTRB(64'hffffffffffffffff),                    // input wire [63 : 0] img_in_TSTRB
  .img_in_TLAST(axis_in.tlast),                    // input wire [0 : 0] img_in_TLAST
  .img_out_TVALID(axis_out.tvalid),                // output wire img_out_TVALID
  .img_out_TREADY(axis_out.tready),                // input wire img_out_TREADY
  .img_out_TDATA(axis_out.tdata),                  // output wire [511 : 0] img_out_TDATA
  .img_out_TKEEP(axis_out.tkeep),                  // output wire [63 : 0] img_out_TKEEP
  .img_out_TSTRB(img_out_TSTRB),                  // output wire [63 : 0] img_out_TSTRB
  .img_out_TLAST(axis_out.tlast),                  // output wire [0 : 0] img_out_TLAST
  .rows(64'd1080),                                    // input wire [31 : 0] rows
  .cols(64'd1920),                                    // input wire [31 : 0] cols
  .threshold(64'd442 /*from xf_harris_tb.cpp*/),   // input wire [31 : 0] threshold
  .k(64'd2621 /*from xf_harris_tb.cpp*/)           // input wire [31 : 0] k
);

endmodule