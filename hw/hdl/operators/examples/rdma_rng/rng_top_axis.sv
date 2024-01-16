module rng_top_axis (
	input clk,
	input rst,
	
	output reg [15:0] arid_m,
	output reg [63:0] araddr_m,
	output reg [7:0]  arlen_m,
	output reg [2:0]  arsize_m,
	output reg        arvalid_m,
	input             arready_m,
	
	input [15:0]  rid_m,
	input [511:0] rdata_m,
	input [1:0]   rresp_m,
	input         rlast_m,
	input         rvalid_m,
	output reg    rready_m,
	
	// output reg [15:0] awid_m,
	// output reg [63:0] awaddr_m,
	// output reg [7:0]  awlen_m,
	// output reg [2:0]  awsize_m,
	// output reg        awvalid_m,
	// input             awready_m,
	
	// output reg [511:0] wdata_m,
	// output reg [63:0]  wstrb_m,
	// output reg         wlast_m,
	// output reg         wvalid_m,
	// input              wready_m,
	
	// input [15:0] bid_m,
	// input [1:0]  bresp_m,
	// input        bvalid_m,
	// output reg   bready_m,
	
	// input        softreg_req_valid,
	// input        softreg_req_isWrite,
	// input [31:0] softreg_req_addr,
	// input [63:0] softreg_req_data,
	
	// output reg        softreg_resp_valid,
	// output reg [63:0] softreg_resp_data
    input [63:0] size_shift_in,
    input [63:0] linear_in,
    input [63:0] read_in,
	input rng_start,

	AXI4SR.m axis_out
);

// // SoftReg signals
// wire softreg_req_read_valid = softreg_req_valid && !softreg_req_isWrite;
// wire softreg_req_write_valid = softreg_req_valid && softreg_req_isWrite;

reg awvalid_m;
reg awready_m;

// RNG signals
reg rng_next [1:0];
wire rng_ready [1:0];
wire [18:0] rng_data [1:0];

// State
reg start [1:0];
reg [3:0] size_shift [1:0];
reg [7:0] txn_len [1:0];
reg [47:0] base_addr [1:0];
reg [47:0] addr [1:0];
reg [47:0] cycles [1:0];
reg [19:0] req_count [2:0];
reg [19:0] resp_count [1:0];
reg [8:0] txn_count0 [2:0];
reg [8:0] txn_count1 [1:0];
reg [8:0] txn_limit [1:0];
reg linear [1:0];
reg [1:0] state [2:0];
reg [5:0] word_count;

// Logic
reg [18:0] addr_index [1:0];
always @(*) begin
	arid_m = 0;
	araddr_m = addr[0];
	arlen_m = txn_len[0];
	arsize_m = 3'b110;
	arvalid_m = 0;
	
	rready_m = 1;
	// awid_m = 0;
	// awaddr_m = addr[1];
	// awlen_m = txn_len[1];
	// awsize_m = 3'b110;
	// awvalid_m = 0;
	
	// wdata_m = {32{rng_data[1][15:0]}};
	// wstrb_m = 64'hFFFFFFFFFFFFFFFF;
	// wlast_m = word_count == txn_len[1];
	// wvalid_m = state[2] == 1;

	awready_m = axis_out.tready;
	axis_out.tdata = {32{rng_data[1][15:0]}};
	axis_out.tlast = word_count == txn_len[1];
	axis_out.tkeep = 64'hFFFFFFFFFFFFFFFF;
	axis_out.tvalid = state[2] == 1;
	axis_out.tid = 0;
	
	// bready_m = 1;
	
	addr_index[0] = linear[0] ? (state[0] == 0 ? 0 : req_count[0]) : rng_data[0];
	addr_index[1] = linear[1] ? (state[1] == 0 ? 0 : req_count[1]) : rng_data[1];
	
	rng_next[0] = 0;
	rng_next[1] = 0;
	
	case (state[0])
		0: rng_next[0] = start[0];
		1: begin
			arvalid_m = rng_ready[0];
			rng_next[0] = arready_m && (txn_count0[0] == txn_limit[0]) && !req_count[0][19];
		end
	endcase
	
	case (state[1])
		0: rng_next[1] = start[1];
		1: begin
			awvalid_m = rng_ready[1];
			rng_next[1] = awready_m && (txn_count0[1] == txn_limit[1]) && !req_count[1][19];
		end
	endcase
end


always @(posedge clk) begin
	// Read logic
	// start[0] <= rng_start && (softreg_req_addr == 32'h00);
	start[0] <= rng_start && read_in;
	if (rvalid_m && rready_m && rlast_m) begin
		txn_count1[0] <= txn_count1[0] + 1;
		if (txn_count1[0] == txn_limit[0]) begin
			txn_count1[0] <= 0;
			resp_count[0] <= resp_count[0] + 1;
		end
	end
	case (state[0])
		0: begin
			if (start[0]) begin
				cycles[0] <= 1;
				txn_count0[0] <= 0;
				txn_count1[0] <= 0;
				req_count[0] <= 1;
				resp_count[0] <= 0;
				state[0] <= 1;
				addr[0] <= base_addr[0] + ((addr_index[0] << 6) << size_shift[0]);
			end
		end
		1: begin
			cycles[0] <= cycles[0] + 1;
			
			if (arvalid_m && arready_m) begin
				addr[0] <= addr[0] + ((txn_len[0] + 1) << 6);
				txn_count0[0] <= txn_count0[0] + 1;
				
				if (txn_count0[0] == txn_limit[0]) begin
					addr[0] <= base_addr[0] + ((addr_index[0] << 6) << size_shift[0]);
					txn_count0[0] <= 0;
					
					if (req_count[0][19]) state[0] <= 2;
					else req_count[0] <= req_count[0] + 1;
				end
			end
		end
		2: begin
			cycles[0] <= cycles[0] + 1;
			
			if (resp_count[0][19]) state[0] <= 0;
		end
	endcase
	
	// Write logic
	// start[1] <= rng_start && (softreg_req_addr == 32'h20);
	start[1] <= rng_start && !read_in;
	// if (bvalid_m && bready_m) begin
    // not sure if this modification is correct
    if (state[1]) begin
        txn_count1[1] <= txn_count1[1] + 1;
        if (txn_count1[1] == txn_limit[1]) begin
            txn_count1[1] <= 0;
            resp_count[1] <= resp_count[1] + 1;
        end
    end

	case (state[1])
		0: begin
			if (start[1]) begin
				cycles[1] <= 1;
				txn_count0[1] <= 0;
				txn_count1[1] <= 0;
				req_count[1] <= 1;
				resp_count[1] <= 0;
				state[1] <= 1;
				addr[1] <= base_addr[1] + ((addr_index[1] << 6) << size_shift[1]);
			end
		end
		1: begin
			cycles[1] <= cycles[1] + 1;
			
			if (awvalid_m && awready_m) begin
				addr[1] <= addr[1] + ((txn_len[1] + 1) << 6);
				txn_count0[1] <= txn_count0[1] + 1;
				
				if (txn_count0[1] == txn_limit[1]) begin
					addr[1] <= base_addr[1] + ((addr_index[1] << 6) << size_shift[1]);
					txn_count0[1] <= 0;
					
					if (req_count[1][19]) state[1] <= 2;
					else req_count[1] <= req_count[1] + 1;
				end
			end
		end
		2: begin
			cycles[1] <= cycles[1] + 1;
			
			if (resp_count[1][19]) state[1] <= 0;
		end
	endcase
	
	// Write data logic
	if (axis_out.tvalid && axis_out.tready) word_count <= axis_out.tlast ? 0 : word_count + 1;
	case (state[2])
		0: begin
			if (start[1]) begin
				txn_count0[2] <= 0;
				req_count[2] <= 1;
				state[2] <= 1;
				word_count <= 0;
			end
		end
		1: begin
			if (axis_out.tvalid && axis_out.tready && axis_out.tlast) begin
				txn_count0[2] <= txn_count0[2] + 1;
				
				if (txn_count0[2] == txn_limit[1]) begin
					txn_count0[2] <= 0;
					
					if (req_count[2][19]) state[2] <= 0;
					else req_count[2] <= req_count[2] + 1;
				end
			end
		end
	endcase
	
	// SoftReg
	if (rng_start) begin
		case (read_in)
			1: begin
				// base_addr[0] <= softreg_req_data[47:0];
				base_addr[0] <= 0;
				// size_shift[0] <= softreg_req_data[51:48];
				size_shift[0] <= size_shift_in;
				if (size_shift_in >= 6) begin
					txn_len[0] <= 8'd63;
					// txn_limit[0] <= (1 << (softreg_req_data[51:48] - 6)) - 1;
					txn_limit[0] <= (1 << (size_shift_in - 6)) - 1;
				end else begin
					// txn_len[0] <= (1 << softreg_req_data[50:48]) - 1;
					txn_len[0] <= (1 << size_shift_in) - 1;
					txn_limit[0] <= 0;
				end
				// linear[0] <= softreg_req_data[52];
				linear[0] <= linear_in;
			end
			0: begin
				// base_addr[1] <= softreg_req_data[47:0];
				base_addr[1] <= 0;
				size_shift[1] <= size_shift_in;
				if (size_shift_in >= 6) begin
					txn_len[1] <= 8'd63;
					txn_limit[1] <= (1 << (size_shift_in - 6)) - 1;
				end else begin
					txn_len[1] <= (1 << size_shift_in) - 1;
					txn_limit[1] <= 0;
				end
				linear[1] <= linear_in;
			end
		endcase
	end

	
	// Reset
	if (rst) begin
		state[0] <= 0;
		state[1] <= 0;
		state[2] <= 0;
	end
end

// Instantiation
rngcore r0(
	.clk(clk),
	.rst(rst),
	
	.next(rng_next[0]),
	.ready(rng_ready[0]),
	.data(rng_data[0])
);

rngcore #(
	.SEED(1<<18)
) r1 (
	.clk(clk),
	.rst(rst),
	
	.next(rng_next[1]),
	.ready(rng_ready[1]),
	.data(rng_data[1])
);

endmodule

