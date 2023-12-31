// Semi-random sequence of unique integers
// Based on math and concept from:
// https://preshing.com/20121224/how-to-generate-a-sequence-of-unique-random-integers/
module rngcore #(
	parameter SEED = 0
) (
	input wire clk,
	input wire rst,
	
	input wire next,
	output wire ready,
	output wire [18:0] data
);
localparam [18:0] prime = (1<<19)-1;

reg [18:0] i_reg, i_reg_;
reg [37:0] i2, i2_;
(* retiming_forward = 1 *) reg [37:0] i2__;
(* retiming_backward = 1 *) reg [18:0] i2_mod_p;
reg [18:0] i2_mod_p_;
reg [5:0] i_decide;

reg [18:0] j_reg, j_reg_;
reg [37:0] j2, j2_;
(* retiming_forward = 1 *) reg [37:0] j2__;
(* retiming_backward = 1 *) reg [18:0] j2_mod_p;
reg [18:0] j2_mod_p_;
reg [5:0] j_decide;

reg [18:0] out_reg;
(* mark_debug = "yes" *) reg [13:0] ready_reg;

wire shift = !ready || next; 
always @(posedge clk) begin
	if (shift) begin
		i_reg <= i_reg + 1;
		i_decide <= {i_reg[18], i_decide[5:1]};
		i_reg_ <= i_reg;
		i2 <= i_reg_*i_reg_;
		i2_ <= i2;
		i2__ <= i2_;
		i2_mod_p <= i2__ % prime;
		i2_mod_p_ <= i2_mod_p;
		j_reg <= 19'h3635 ^ (i_decide[0] ? (prime - i2_mod_p_) : i2_mod_p_);
		j_decide <= {j_reg[18], j_decide[5:1]};
		j_reg_ <= j_reg;
		j2 <= j_reg_*j_reg_;
		j2_ <= j2;
		j2__ <= j2_;
		j2_mod_p <= j2__ % prime;
		j2_mod_p_ <= j2_mod_p;
		out_reg <= j_decide[0] ? (prime - j2_mod_p_) : j2_mod_p_;
		
		ready_reg <= {1'b1, ready_reg[13:1]};
	end
	
	if (~rst) begin
		i_reg <= SEED;
		ready_reg <= 0;
		out_reg <= 0;
		j2_mod_p <= 0;
		j2_mod_p_ <= 0;
	end
end

assign ready = ready_reg[0];
assign data = out_reg;

endmodule

