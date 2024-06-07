`timescale 1ns / 1ps


module matmul_ab #(
    parameter SIZE=64,
    parameter MEM_WIDTH=4096
)
(
    input aclk,
    input aresetn,
    
    AXI4SR.s                 axis_in,
    AXI4SR.m                 axis_out 
);

localparam integer LS = $clog2(SIZE);
localparam integer AXI_INTS = 8;
localparam integer AXITX_PER_ROW = SIZE/AXI_INTS;
localparam SZSZ = SIZE*SIZE;
localparam READ_OPS = SZSZ/AXI_INTS;

logic [6:0] state;
logic [2:0] mul_state;
logic [1:0] out_state;
logic ul_resetn = 0;
 
reg [MEM_WIDTH/8-1 : 0] aa_wea;    
reg [LS-1 : 0] aa_addra;    
reg [MEM_WIDTH-1 : 0] aa_dina;  
reg [MEM_WIDTH-1 : 0] aa_douta;           

reg [MEM_WIDTH/8-1 : 0] dst_wea;    
reg [LS-1 : 0] dst_addra;   
reg [MEM_WIDTH-1 : 0] dst_dina;  
reg [MEM_WIDTH-1 : 0] dst_douta;    

reg [MEM_WIDTH/8-1 : 0] bb_wea;    
reg [LS-1 : 0] bb_addra;    
reg [MEM_WIDTH-1 : 0] bb_dina;  
reg [MEM_WIDTH-1 : 0] bb_douta;              

blk_mem_gen_c0_1 aa (
  .clka(aclk),            // input wire clka
  //.rsta(1'b0/*~aresetn*/),            // input wire rsta
  //.ena(1'b1 /*aa_ena*/),              // input wire ena
  .wea(aa_wea),              // input wire [127 : 0] wea
  .addra(aa_addra),          // input wire [9 : 0] addra
  .dina(aa_dina),            // input wire [1023 : 0] dina
  .douta(aa_douta)          // output wire [1023 : 0] douta
  //.rsta_busy(rsta_busy)  // output wire rsta_busy
);
blk_mem_gen_c0_1 bb (
  .clka(aclk),            // input wire clka
  //.rsta(1'b0/*~aresetn*/),            // input wire rsta
  //.ena(1'b1 /*aa_ena*/),              // input wire ena
  .wea(bb_wea),              // input wire [127 : 0] wea
  .addra(bb_addra),          // input wire [9 : 0] addra
  .dina(bb_dina),            // input wire [1023 : 0] dina
  .douta(bb_douta)          // output wire [1023 : 0] douta
  //.rsta_busy(rsta_busy)  // output wire rsta_busy
);
blk_mem_gen_c0_1 dst (
  .clka(aclk),            // input wire clka
  //.rsta(1'b0/*~aresetn*/),            // input wire rsta
  //.ena(1'b1 /*dst_ena*/),              // input wire ena
  .wea(dst_wea),              // input wire [127 : 0] wea
  .addra(dst_addra),          // input wire [9 : 0] addra
  .dina(dst_dina),            // input wire [1023 : 0] dina
  .douta(dst_douta)          // output wire [1023 : 0] douta
  //.rsta_busy(rsta_busy)  // output wire rsta_busy
);

reg [MEM_WIDTH-1 : 0] at_aa;
reg [63 : 0] at_bb[SIZE];
reg [2*LS-1 : 0] at_addr;
reg at_valid;
reg [2*LS-1 : 0] at_out_addr;
reg [63:0] at_out_sum;
reg at_out_valid;

addtree #(
    .INTS(SIZE),
    .ADDR_BITS(2*LS))
at(
    .aclk(aclk),
    .aresetn(ul_resetn),
    .aa(at_aa), 
    .bb(at_bb),
    .addr(at_addr),
    .valid(at_valid),
    .out_addr(at_out_addr),
    .out_sum(at_out_sum),
    .out_valid(at_out_valid)
);


logic [2*LS-1:0] rdptr;

logic [2*LS-1:0] cptr;
logic [LS-1:0] c_row;
logic [LS-1:0] c_col;
assign c_col = cptr[2*LS-1 : LS];
assign c_row = cptr[LS-1 : 0];

logic [63:0] col0[SIZE];
(* shreg_extract = "yes" *)
logic [63:0] col1[SIZE];

reg dst_complete;

logic [2*LS-1:0] wrptr;

always @(posedge aclk) begin
    ul_resetn <= aresetn;
end
 
always @(posedge aclk) begin
    if(~ul_resetn) begin
        state <= 7'b0000001;
    end
    else begin
        aa_wea <= 0;
        bb_wea <= 0;
        dst_wea <= 0;
        at_valid <= 0;

        if(at_out_valid) begin
            dst_addra <= at_out_addr/SIZE;
            dst_wea <= 64'hff << ((at_out_addr%SIZE)*8);
            dst_dina <= at_out_sum << ((at_out_addr%SIZE)*64);
            dst_complete <= (at_out_addr == SIZE*SIZE-1);
        end
    
        case(state)
        7'b0000001: begin
            state <= 7'b0000010;
            mul_state <= 3'b001;
            rdptr <= 0;
            cptr <= 0;
            wrptr <= 0;
            dst_complete <= 0;
        end    
        7'b0000010: begin
            if(axis_in.tvalid) begin
                aa_addra <= rdptr / AXITX_PER_ROW;
                aa_dina <= axis_in.tdata << ((rdptr%AXITX_PER_ROW)*512);
                aa_wea <= 64'hffffffffffffffff << ((rdptr%AXITX_PER_ROW)*64);

                rdptr <= rdptr + 1;
                if(rdptr == READ_OPS-1) begin
                    state <= state<<1;
                    rdptr <= 0;
                end
            end
        end

        7'b0000100: begin
            if(axis_in.tvalid) begin
                bb_addra <= rdptr / AXITX_PER_ROW;
                bb_dina <= axis_in.tdata << ((rdptr%AXITX_PER_ROW)*512);
                bb_wea <= 64'hffffffffffffffff << ((rdptr%AXITX_PER_ROW)*64);

                if(rdptr%AXITX_PER_ROW==0) begin
                    //col1[rdptr/AXITX_PER_ROW] <= axis_in.tdata[63:0];
                    for(integer i=0; i<SIZE-1; i++) begin
                        col1[i] <= col1[i+1];
                    end
                    col1[SIZE-1] <= axis_in.tdata[63:0];
                end

                rdptr <= rdptr + 1;
                if(rdptr == READ_OPS-1) begin
                    state <= state<<1;
                    rdptr <= 0;
                end
            end
        end
        
        7'b0001000: begin
            if(mul_state == 3'b001) begin
                aa_addra <= 0;
                bb_addra <= 0;
                col0 <= col1;
                //col1 <= 0;
                mul_state <= mul_state<<1;
            end
            
            if(mul_state == 3'b010) begin
                mul_state <= mul_state<<1;
            end
            
            if(mul_state == 3'b100) begin
                at_aa <= aa_douta;
                at_bb <= col0;
                at_addr <= {c_row, c_col};
                at_valid <= 1;

                if(c_col < SIZE-1) begin
                    //col1[c_row] <= bb_douta[(c_col+1)*64+:64];
                    for(integer i=0; i<SIZE-1; i++) begin
                        col1[i] <= col1[i+1];
                    end
                    col1[SIZE-1] <= bb_douta[(c_col+1)*64+:64];
                end

                if(c_row < SIZE-1) begin
                    aa_addra <= c_row+1;
                    bb_addra <= c_row+1;
                    mul_state <= mul_state>>1;
                end else begin
                    mul_state <= 3'b001;
                end

                cptr <= cptr+1;
                if(cptr == SIZE*SIZE-1)
                    state <= state<<1;
            end
        end
        
        7'b0010000: begin
            if(dst_complete) begin
                dst_addra <= 0;
                out_state <= 1'b01;
                state <= state<<1;
            end;
        end

        7'b0100000: begin
            if(out_state == 2'b01) begin
                out_state <= 2'b10;
            end

            if(out_state == 2'b10) begin
                if(axis_out.tready && axis_out.tvalid) begin
                    wrptr <= wrptr+1;
                    if(wrptr == READ_OPS-1)
                        state <= state<<1;
                    else if((wrptr+1) % AXITX_PER_ROW == 0) begin
                        dst_addra <= (wrptr+1)/AXITX_PER_ROW;
                        out_state <= 2'b01;
                    end
                end
            end
        end

        7'b1000000: begin
            state <= 7'b0000001;
        end
        endcase
    end
end


assign axis_in.tready = state == 7'b0000010 || state == 7'b0000100;

always_comb begin
    axis_out.tvalid = state==7'b0100000 && out_state==2'b10;
    axis_out.tlast = wrptr==READ_OPS-1;
    axis_out.tkeep = 64'hffffffffffffffff;
    axis_out.tid = 0;
    axis_out.tdata[511:0] = dst_douta[512*(wrptr%AXITX_PER_ROW)+:512];
end


endmodule
