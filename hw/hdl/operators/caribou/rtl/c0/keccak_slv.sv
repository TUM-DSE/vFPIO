`timescale 1ns / 1ps

module keccak_slv(
    input aclk,
    input aresetn,
    
    AXI4SR.s                 axis_in,
    AXI4SR.m                 axis_out
);

reg ul_resetn;
reg [2:0] ul_reset_state;

                            
wire m_axis_tvalid;        
wire m_axis_tready;        
wire [31 : 0] m_axis_tdata;
wire [3 : 0] m_axis_tkeep; 
wire m_axis_tlast;                     


axis_dwidth_converter_c0_1 axis_dwidth_conv (
  .aclk(aclk),                    // input wire aclk
  .aresetn(ul_resetn),              // input wire aresetn
  .s_axis_tvalid(axis_in.tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(axis_in.tready),  // output wire s_axis_tready
  .s_axis_tdata(axis_in.tdata),    // input wire [511 : 0] s_axis_tdata
  .s_axis_tkeep(axis_in.tkeep),    // input wire [63 : 0] s_axis_tkeep
  .s_axis_tlast(axis_in.tlast),    // input wire s_axis_tlast
  .m_axis_tvalid(m_axis_tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(m_axis_tready),  // input wire m_axis_tready
  .m_axis_tdata(m_axis_tdata),    // output wire [63 : 0] m_axis_tdata
  .m_axis_tkeep(m_axis_tkeep),    // output wire [7 : 0] m_axis_tkeep
  .m_axis_tlast(m_axis_tlast)    // output wire m_axis_tlast
);


reg [31:0] word;
reg word_valid;
reg word_last;
reg [1:0] byte_num;
reg at_empty_block;

reg [511:0] out_hash;
reg out_ready;
reg out_complete;
wire out_transmit;

keccak keccak_top (
    .clk(aclk),
    .reset(~ul_resetn),
    .in(word),
    .byte_num(byte_num),
    .in_ready(word_valid),
    .is_last(word_last),
    .buffer_full(buffer_full),
    .out(out_hash),
    .out_ready(out_ready)
);


assign word[0+:8]  = m_axis_tdata[24+:8];
assign word[8+:8]  = m_axis_tdata[16+:8];
assign word[16+:8] = m_axis_tdata[8+:8];
assign word[24+:8] = m_axis_tdata[0+:8];

assign m_axis_tready = ~buffer_full && ul_resetn;
assign byte_num = (m_axis_tvalid && m_axis_tlast) ? ($countones(m_axis_tkeep) & 2'b11) : 2'b00;
assign need_empty_block = m_axis_tvalid && m_axis_tlast && ($countones(m_axis_tkeep) == 3'd4);
assign word_last = (m_axis_tlast && ~need_empty_block) || at_empty_block;
assign word_valid = m_axis_tvalid || at_empty_block;

assign out_transmit = axis_out.tvalid && axis_out.tready;

    
always_ff @(posedge aclk) begin

    ul_resetn <= (aresetn==1'b1) && (ul_reset_state==3'b000);
     
    if((aresetn == 1'b0) || (ul_reset_state == 3'b111)) begin
            
        at_empty_block <= 0;
        out_complete <= 0;
        ul_reset_state <= 0;
        
    end else begin

        //INPUT 
        if(~buffer_full && at_empty_block)
            at_empty_block <= 0;
        
        if(need_empty_block)
            at_empty_block <= 1;
          
        //OUTPUT
        if (out_complete) begin
            ul_reset_state <= ul_reset_state + 1;
        end
          
        if(out_transmit) begin
            axis_out.tvalid <= 1'b0;
            out_complete <= 1'b1;
        end        
        
        if(out_ready && ~out_transmit && ~out_complete) begin
            axis_out.tdata <= out_hash;
            axis_out.tvalid <= 1'b1;
            axis_out.tlast <= 1'b1;
            axis_out.tkeep <= 64'hffffffffffffffff;
            axis_out.tid <= 0;
         end
    end
end


endmodule
