`timescale 1ns / 1ps

module hls4ml_wrapper(
    input aclk,
    input aresetn,
    
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
);

reg ul_resetn = 0;

(* mark_debug = "yes" *) reg ap_start = 0;
(* mark_debug = "yes" *) logic ap_done;
(* mark_debug = "yes" *) logic ap_ready;
(* mark_debug = "yes" *) logic ap_idle;

(* mark_debug = "yes" *) logic input_2_TVALID;
(* mark_debug = "yes" *) logic input_2_TREADY;
(* mark_debug = "yes" *) logic [47 : 0] input_2_TDATA;
logic layer25_out_TVALID;
logic layer25_out_TREADY;
logic [159 : 0] layer25_out_TDATA;

(* mark_debug = "yes" *) logic axis_in_tavlid;
(* mark_debug = "yes" *) logic axis_in_tready;
(* mark_debug = "yes" *) logic [511:0] axis_in_tdata;
(* mark_debug = "yes" *) logic axis_in_tlast;

(* mark_debug = "yes" *) logic axis_out_tavlid;
(* mark_debug = "yes" *) logic axis_out_tready;
(* mark_debug = "yes" *) logic [511:0] axis_out_tdata;
(* mark_debug = "yes" *) logic axis_out_tlast;

assign axis_in_tavlid = axis_in.tvalid;
assign axis_in_tready = axis_in.tready;
assign axis_in_tdata = axis_in.tdata;
assign axis_in_tlast = axis_in.tlast;

assign axis_out_tavlid = axis_out.tvalid;
assign axis_out_tready = axis_out.tready;
assign axis_out_tdata = axis_out.tdata;
assign axis_out_tlast = axis_out.tlast;


assign axis_out.tid = 0;
assign axis_out.tdata[511:160] = 0;
assign axis_out.tkeep = 64'hffffffffffffffff; //64'hfffff;
assign axis_out.tlast = 0; //1;

always_ff @(posedge aclk) begin
    ul_resetn <= aresetn;
    if(ap_idle) begin
        ap_start <= 1;
    end
    if(ap_ready)
        ap_start <= 0;
end

axis_dwidth_converter_c1 dwidth_conv (
  .aclk(aclk),                    // input wire aclk
  .aresetn(ul_resetn),              // input wire aresetn
  .s_axis_tvalid(axis_in.tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(axis_in.tready),  // output wire s_axis_tready
  .s_axis_tdata(axis_in.tdata),    // input wire [511 : 0] s_axis_tdata
  .m_axis_tvalid(input_2_TVALID),  // output wire m_axis_tvalid
  .m_axis_tready(input_2_TREADY),  // input wire m_axis_tready
  .m_axis_tdata(input_2_TDATA)    // output wire [47 : 0] m_axis_tdata
);

hls4ml_0 hls4ml_inst (
  .input_2_TVALID(input_2_TVALID),          // input wire input_2_TVALID
  .input_2_TREADY(input_2_TREADY),          // output wire input_2_TREADY
  .input_2_TDATA(input_2_TDATA),            // input wire [47 : 0] input_2_TDATA
  .layer25_out_TVALID(axis_out.tvalid),  // output wire layer25_out_TVALID
  .layer25_out_TREADY(axis_out.tready),  // input wire layer25_out_TREADY
  .layer25_out_TDATA(axis_out.tdata[159:0]),    // output wire [159 : 0] layer25_out_TDATA
  .ap_clk(aclk),                          // input wire ap_clk
  .ap_rst_n(ul_resetn),                      // input wire ap_rst_n
  .ap_start(ap_start),                      // input wire ap_start
  .ap_done(ap_done),                        // output wire ap_done
  .ap_ready(ap_ready),                      // output wire ap_ready
  .ap_idle(ap_idle)                        // output wire ap_idle
);

endmodule
