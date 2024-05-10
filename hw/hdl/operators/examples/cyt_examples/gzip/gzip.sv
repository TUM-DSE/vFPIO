`timescale 1ns / 1ps

module gzip(
    input aclk,
    input aresetn,
    
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
);

logic w_clk250;
logic w_clk125;

clk_wiz_0 clkwiz_inst
(
    // Clock out ports
    .clk_out1(w_clk250),     // output clk_out1
    .clk_out2(w_clk125),     // output clk_out2
   // Clock in ports
    .clk_in1(aclk)      // input clk_in1
);


reg s_resetn = 0;
assign axis_out.tid = 0;

always @(posedge w_clk125) begin
    s_resetn <= aresetn;
end


wire dwcin_m_axis_tvalid;         
wire dwcin_m_axis_tready;          
wire [255 : 0] dwcin_m_axis_tdata;
wire [31 : 0] dwcin_m_axis_tkeep; 
wire dwcin_m_axis_tlast;

axis_dwidth_converter_in_2 dwidth_conv_in (
  .aclk(aclk),                    // input wire aclk
  .aresetn(aresetn),              // input wire aresetn
  .s_axis_tvalid(axis_in.tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(axis_in.tready),  // output wire s_axis_tready
  .s_axis_tdata(axis_in.tdata),    // input wire [511 : 0] s_axis_tdata
  .s_axis_tkeep(axis_in.tkeep),    // input wire [63 : 0] s_axis_tkeep
  .s_axis_tlast(axis_in.tlast),    // input wire s_axis_tlast
  .m_axis_tvalid(dwcin_m_axis_tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(dwcin_m_axis_tready),  // input wire m_axis_tready
  .m_axis_tdata(dwcin_m_axis_tdata),    // output wire [255 : 0] m_axis_tdata
  .m_axis_tkeep(dwcin_m_axis_tkeep),    // output wire [31 : 0] m_axis_tkeep
  .m_axis_tlast(dwcin_m_axis_tlast)    // output wire m_axis_tlast
);


wire ccin_m_axis_tvalid;          
wire ccin_m_axis_tready;           
wire [255 : 0] ccin_m_axis_tdata; 
wire [31 : 0] ccin_m_axis_tkeep;  
wire ccin_m_axis_tlast;
            
axis_clock_converter_2 clock_conv_in (
  .s_axis_aresetn(aresetn),  // input wire s_axis_aresetn
  .m_axis_aresetn(s_resetn),  // input wire m_axis_aresetn
  .s_axis_aclk(aclk),        // input wire s_axis_aclk
  .s_axis_tvalid(dwcin_m_axis_tvalid),    // input wire s_axis_tvalid
  .s_axis_tready(dwcin_m_axis_tready),    // output wire s_axis_tready
  .s_axis_tdata(dwcin_m_axis_tdata),      // input wire [255 : 0] s_axis_tdata
  .s_axis_tkeep(dwcin_m_axis_tkeep),      // input wire [31 : 0] s_axis_tkeep
  .s_axis_tlast(dwcin_m_axis_tlast),      // input wire s_axis_tlast
  .m_axis_aclk(w_clk125),        // input wire m_axis_aclk
  .m_axis_tvalid(ccin_m_axis_tvalid),    // output wire m_axis_tvalid
  .m_axis_tready(ccin_m_axis_tready),    // input wire m_axis_tready
  .m_axis_tdata(ccin_m_axis_tdata),      // output wire [255 : 0] m_axis_tdata
  .m_axis_tkeep(ccin_m_axis_tkeep),      // output wire [31 : 0] m_axis_tkeep
  .m_axis_tlast(ccin_m_axis_tlast)      // output wire m_axis_tlast
);


wire ll_m_axis_tvalid;           
wire ll_m_axis_tready;            
wire [255 : 0] ll_m_axis_tdata;
wire [31 : 0] ll_m_axis_tkeep;
wire [35 : 0] ll_m_axis_tuser;   
wire ll_m_axis_tlast;

ll_compress_2 ll_compress (
  .s_aclk_250(w_clk125),        // input wire s_aclk_250
  .s_aclk_500(w_clk250),        // input wire s_aclk_500
  .clk_hf(w_clk125),                // input wire clk_hf
  .s_aresetn(s_resetn),          // input wire s_aresetn
  .s_axis_tvalid(ccin_m_axis_tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(ccin_m_axis_tready),  // output wire s_axis_tready
  .s_axis_tdata(ccin_m_axis_tdata),    // input wire [255 : 0] s_axis_tdata
  .s_axis_tkeep(ccin_m_axis_tkeep),    // input wire [31 : 0] s_axis_tkeep
  .s_axis_tlast(ccin_m_axis_tlast),    // input wire s_axis_tlast
  .m_axis_tvalid(ll_m_axis_tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(ll_m_axis_tready),  // input wire m_axis_tready
  .m_axis_tdata(ll_m_axis_tdata),    // output wire [255 : 0] m_axis_tdata
  .m_axis_tkeep(ll_m_axis_tkeep),    // output wire [31 : 0] m_axis_tkeep
  .m_axis_tuser(ll_m_axis_tuser),    // output wire [35 : 0] m_axis_tuser
  .m_axis_tlast(ll_m_axis_tlast)    // output wire m_axis_tlast
);
    
    
wire ccout_m_axis_tvalid;         
wire ccout_m_axis_tready;         
wire [255 : 0] ccout_m_axis_tdata;
wire [31 : 0] ccout_m_axis_tkeep; 
wire ccout_m_axis_tlast;

axis_clock_converter_2 clock_conv_out (
  .s_axis_aresetn(s_resetn),  // input wire s_axis_aresetn
  .m_axis_aresetn(aresetn),  // input wire m_axis_aresetn
  .s_axis_aclk(w_clk125),        // input wire s_axis_aclk
  .s_axis_tvalid(ll_m_axis_tvalid),    // input wire s_axis_tvalid
  .s_axis_tready(ll_m_axis_tready),    // output wire s_axis_tready
  .s_axis_tdata(ll_m_axis_tdata),      // input wire [255 : 0] s_axis_tdata
  .s_axis_tkeep(ll_m_axis_tkeep),      // input wire [31 : 0] s_axis_tkeep
  .s_axis_tlast(ll_m_axis_tlast),      // input wire s_axis_tlast
  .m_axis_aclk(aclk),        // input wire m_axis_aclk
  .m_axis_tvalid(ccout_m_axis_tvalid),    // output wire m_axis_tvalid
  .m_axis_tready(ccout_m_axis_tready),    // input wire m_axis_tready
  .m_axis_tdata(ccout_m_axis_tdata),      // output wire [255 : 0] m_axis_tdata
  .m_axis_tkeep(ccout_m_axis_tkeep),      // output wire [31 : 0] m_axis_tkeep
  .m_axis_tlast(ccout_m_axis_tlast)      // output wire m_axis_tlast
);

axis_dwidth_converter_out_2 dwidth_conv_out (
  .aclk(aclk),                    // input wire aclk
  .aresetn(aresetn),              // input wire aresetn
  .s_axis_tvalid(ccout_m_axis_tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(ccout_m_axis_tready),  // output wire s_axis_tready
  .s_axis_tdata(ccout_m_axis_tdata),    // input wire [255 : 0] s_axis_tdata
  .s_axis_tkeep(ccout_m_axis_tkeep),    // input wire [31 : 0] s_axis_tkeep
  .s_axis_tlast(ccout_m_axis_tlast),    // input wire s_axis_tlast
  .m_axis_tvalid(axis_out.tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(axis_out.tready),  // input wire m_axis_tready
  .m_axis_tdata(axis_out.tdata),    // output wire [511 : 0] m_axis_tdata
  .m_axis_tkeep(axis_out.tkeep),    // output wire [63 : 0] m_axis_tkeep
  .m_axis_tlast(axis_out.tlast)    // output wire m_axis_tlast
);

endmodule
