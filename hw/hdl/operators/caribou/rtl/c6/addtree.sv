`timescale 1ns / 1ps

module addtree #(
    parameter INTS=8,
    parameter INT_BITS=64,
    parameter BITS=INTS*INT_BITS,
    parameter ADDR_BITS=10
) (
    input aclk,
    input aresetn,
    input [BITS-1:0] aa,
    input [INT_BITS-1:0] bb[INTS],
    input [ADDR_BITS-1:0] addr,
    input valid,
    output reg [ADDR_BITS-1:0] out_addr,
    output reg [INT_BITS-1:0] out_sum,
    output reg out_valid
);

localparam LEVELS = $clog2(INTS)+1;

reg [INT_BITS-1:0] tree [2*INTS-1];
reg [ADDR_BITS-1:0] addr_tree [LEVELS];
reg valid_tree [LEVELS];

always @(posedge aclk) begin

    if(aresetn == 0) begin
        out_valid <= 0;
        for(integer i=0; i<INTS; i++)
            valid_tree[i] <= 0;
    end 
    else begin

        out_valid <= valid_tree[0];
        out_addr <= addr_tree[0];
        out_sum <= tree[0];

        for(integer i=0; i<INTS-1; i++) begin
            tree[i] <= tree[i*2+1] + tree[i*2+2];
        end
        for(integer i=0; i<LEVELS-1; i++) begin
            addr_tree[i] <= addr_tree[i+1];
            valid_tree[i] <= valid_tree[i+1];
        end
        
        addr_tree[LEVELS-1] <= addr;
        valid_tree[LEVELS-1] <= valid;
        for(integer i=0; i<INTS; i++) begin
            tree[INTS-1+i] <= signed'(aa[i*INT_BITS+:INT_BITS]) * signed'(bb[i]);
        end

    end
    
end

endmodule
