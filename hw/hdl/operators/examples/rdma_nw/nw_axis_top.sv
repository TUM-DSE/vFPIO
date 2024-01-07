`timescale 1ns / 1ps



module width_down #(
	parameter IN_W = 512,
	parameter OUT_W = 128
) (
	input clk,
	input rst,
	
	input [IN_W-1:0] idata,
	input ivalid,
	output reg iready,
	
	output reg [OUT_W-1:0] odata,
	output reg ovalid,
	input oready
);
// assumes widths are powers of 2
localparam D_W = IN_W;
localparam W_RATIO = IN_W/OUT_W;
localparam R_W = $clog2(W_RATIO);

reg [D_W-1:0] data;
reg valid;

reg [R_W-1:0] idx;
reg last;
always @(*) begin
	last = idx == (W_RATIO-1);
	
	iready = !valid;
end
always @(posedge clk) begin
	if (ivalid && iready) begin
		data <= idata;
		valid <= 1;
	end
	
	if ((!ovalid) || oready) begin
		odata <= data[OUT_W*idx +: OUT_W];
		ovalid <= valid;
		if (valid) begin
			idx <= idx + 1;
			if (last) valid <= 0;
		end
	end
	
	if (rst) begin
		valid <= 0;
		ovalid <= 0;
		idx <= 0;
	end
end

endmodule


module width_up #(
	parameter IN_W = 8,
	parameter OUT_W = 512
) (
	input clk,
	input rst,
	
	input [IN_W-1:0] idata,
	input ilast,
	input ivalid,
	
	output reg [OUT_W-1:0] odata,
	output reg ovalid
);
// assumes widths are powers of 2
localparam W_RATIO = OUT_W/IN_W;
localparam R_W = $clog2(W_RATIO);

reg [R_W-1:0] idx;
wire last = idx == (W_RATIO-1);

always @(posedge clk) begin
	odata[IN_W*idx +: IN_W] <= idata;
	
	ovalid <= 0;
	if (ivalid) begin
		idx <= idx + 1;
		if (ilast || last) ovalid <= 1;
		if (ilast) idx <= 0;
	end
	
	if (rst) begin
		ovalid <= 0;
		idx <= 0;
	end
end

endmodule


module nw_axis_top (
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
	
	/*output reg [15:0] awid_m,
	output reg [63:0] awaddr_m,
	output reg [7:0]  awlen_m,
	output reg [2:0]  awsize_m,
	output reg        awvalid_m,
	input             awready_m,
	
	output reg [511:0] wdata_m,
	output reg [63:0]  wstrb_m,
	output reg         wlast_m,
	output reg         wvalid_m,
	input              wready_m,
	
	input [15:0] bid_m,
	input [1:0]  bresp_m,
	input        bvalid_m,
	output reg   bready_m,
	
	input        softreg_req_valid,
	input        softreg_req_isWrite,
	input [31:0] softreg_req_addr,
	input [63:0] softreg_req_data,
	
	output        softreg_resp_valid,
	output [63:0] softreg_resp_data,
	*/

	input [63:0] s0_words_in,
	input [63:0] s1_words_in,
	input [63:0] sc_count_in,
	input [63:0] sc_words_in,
	input start,

	AXI4SR.m axis_out
);

localparam RATIO = 4;
localparam LOG_R = $clog2(RATIO);
localparam STR_W = 512/RATIO;
localparam SCORE_W = 8;
localparam SCORE_RATIO = 512/SCORE_W;

//// Input path
// S0 data FIFO signals
reg s0f_wrreq;
reg [511:0] s0f_din;
wire s0f_full;
wire s0f_rdreq;
wire [511:0] s0f_dout;
wire s0f_empty;

// S1 data FIFO signals
reg s1f_wrreq;
reg [511:0] s1f_din;
wire s1f_full;
wire s1f_rdreq;
wire [511:0] s1f_dout;
wire s1f_empty;

// State and signals
//reg [63:0] s0_base_addr;
//reg [31:0] s0_base_words;
reg [63:0] s0_addr;
reg [31:0] s0_words;
//reg [63:0] s1_base_addr;
//reg [31:0] s1_base_words;
reg [63:0] s1_addr;
reg [31:0] s1_words;
reg [15:0] s1_credit;
reg [15:0] s1_credit_add;

reg [7:0]  nw_state;
reg [LOG_R-1:0] r_count;

// Logic
reg [7:0] s1_len_addr, s1_len;

always @(*) begin
	arid_m = 0;
	araddr_m = 0;
	arlen_m = 0;
	arsize_m = 3'b110;
	arvalid_m = 0;
	
	rready_m = 1;
	
	s0f_wrreq = rvalid_m && (rid_m == 0);
	s0f_din = rdata_m;
	
	s1f_wrreq = rvalid_m && (rid_m == 1);
	s1f_din = rdata_m;
	
	s1_len_addr = 8'd64 - s1_addr[11:6];
	s1_len = (s1_words < s1_len_addr) ? s1_words : s1_len_addr;
	case(nw_state)
		1: begin
			arid_m = 0;
			araddr_m = s0_addr;
			arlen_m = 0;
			arvalid_m = 1;
		end
		2: begin
			arid_m = 1;
			araddr_m = s1_addr;
			arlen_m = s1_len - 1;
			arvalid_m = (s1_credit >= 64);
		end
	endcase
end
always @(posedge clk) begin
	s1_credit <= s1_credit + s1_credit_add;
	
	case(nw_state)
		0: begin
			if(start) begin
				// Wait for start signal
				s0_addr <= 0;
				s0_words <= s0_words_in;
				s1_addr <= 64*s0_words_in;
				s1_words <= s1_words_in;
				r_count <= 0;
				s1_credit <= 256;
				//sc_total <= sc_count_in;
				//scd_words <= sc_words_in;
				nw_state <= 1;
			end
		end
		1: begin
			// Read word for S0
			if (arready_m) begin
				s0_addr <= s0_addr + 64;
				s0_words <= s0_words - 1;
				
				nw_state <= 2;
			end
		end
		2: begin
			// Read pages for S1
			if (arready_m && arvalid_m) begin
				s1_addr <= s1_addr + (s1_len << 6);
				s1_words <= s1_words - s1_len;
				s1_credit <= s1_credit - s1_len + s1_credit_add;
			end
			if (s1_words == 0) nw_state <= 3;
		end
		3: begin
			s1_addr <= s0_words_in*64;
			s1_words <= s1_words_in;
			
			r_count <= r_count + 1;
			if (r_count < RATIO-1) begin
				nw_state <= 2;
			end else if (s0_words > 0) begin
				nw_state <= 1;
			end else begin
				nw_state <= 0;
			end
		end
	endcase
	
	if (rst) begin
		nw_state <= 0;
		//s1_credit <= 128;
	end
end

// Instantiations
HullFIFO #(
	.TYPE(0),
	.WIDTH(512),
	.LOG_DEPTH(2)
) s0_data_fifo (
	.clock(clk),
	.reset_n(~rst),
	.wrreq(s0f_wrreq),
	.data(s0f_din),
	.full(s0f_full),
	.rdreq(s0f_rdreq),
	.q(s0f_dout),
	.empty(s0f_empty)
);
HullFIFO #(
	.TYPE(3),
	.WIDTH(512),
	.LOG_DEPTH(8)
) s1_data_fifo (
	.clock(clk),
	.reset_n(~rst),
	.wrreq(s1f_wrreq),
	.data(s1f_din),
	.full(s1f_full),
	.rdreq(s1f_rdreq),
	.q(s1f_dout),
	.empty(s1f_empty)
);



//// NW Core
// State and signals
wire s0_valid;
wire s1_valid;
wire s_valid = s0_valid && s1_valid;

wire [STR_W-1:0] s0_data;
wire [STR_W-1:0] s1_data;

reg [31+LOG_R:0] s0_count;
wire s0_ready = s1_valid && ((s0_count/RATIO) == s1_words_in);
wire s1_ready = s0_valid;

reg [35:0] sc_count;
reg [35:0] sc_total;
wire last_score = sc_count == sc_total;
wire score_valid;
wire signed [SCORE_W-1:0] score;
wire wide_score_valid;
wire [511:0] wide_score;

// Logic
always @(posedge clk) begin	
	if (s_valid) s0_count <= s0_count + 1;
	if (s0_ready && s1_ready) begin
		s0_count <= 1;
	end
	if (score_valid) begin
		if (last_score) begin
			sc_count <= 1;
		end else begin
			sc_count <= sc_count + 1;
		end
	end
	
	if(start) begin
	   sc_total <= sc_count_in;
	end
	
	if (rst) begin
		s0_count <= 1;
		sc_count <= 1;
	end
end

// Instantiations
width_down s0_wd (
	.clk(clk),
	.rst(rst),
	.idata(s0f_dout),
	.ivalid(!s0f_empty),
	.iready(s0f_rdreq),
	.odata(s0_data),
	.ovalid(s0_valid),
	.oready(s0_ready)
);
width_down s1_wd (
	.clk(clk),
	.rst(rst),
	.idata(s1f_dout),
	.ivalid(!s1f_empty),
	.iready(s1f_rdreq),
	.odata(s1_data),
	.ovalid(s1_valid),
	.oready(s1_ready)
);
Grid #(
	.S_LEN(STR_W/2),
	.C_WIDTH(2),
	.S_WIDTH(SCORE_W)
) dut (
	.clk(clk),
	.rst(rst),
	
	.valid_in(s_valid),
	.t_str(s0_data),
	.l_str(s1_data),
	
	.valid_out(score_valid),
	.score(score)
);
width_up #(
	.IN_W(SCORE_W)
) s_wu (
	.clk(clk),
	.rst(rst),
	
	.idata(score),
	.ilast(last_score),
	.ivalid(score_valid),
	
	.odata(wide_score),
	.ovalid(wide_score_valid)
);


//// Output path
// Wide score FIFO signals
reg wsf_wrreq;
reg [511:0] wsf_din;
wire wsf_full;
reg wsf_rdreq;
wire [511:0] wsf_dout;
wire wsf_empty;

// State and signals
//reg [63:0] sc_addr;
//reg [31:0] sc_words;
//reg [63:0] scd_addr;
reg [31:0] scd_words;

// Logic
reg [7:0] sc_len_addr, sc_len;
always @(*) begin
	wsf_wrreq = wide_score_valid;
	wsf_din = wide_score;
	/*wsf_rdreq = wready_m;
	
	sc_len_addr = 8'd64 - sc_addr[11:6];
	sc_len = (sc_words < sc_len_addr) ? sc_words : sc_len_addr;
	
	awid_m = 0;
	awaddr_m = sc_addr;
	awlen_m = sc_len-1;
	awsize_m = 3'b110;
	awvalid_m = (sc_words > 0);
	
	wdata_m = wsf_dout;
	wstrb_m = 64'hFFFFFFFFFFFFFFFF;
	wlast_m = (scd_addr[11:6] == 6'h3F) || (scd_words == 1);
	wvalid_m = !wsf_empty;
	*/

	wsf_rdreq = axis_out.tready;
	axis_out.tdata = wsf_dout;
	axis_out.tlast = scd_words == 1;
	axis_out.tkeep = 64'hFFFFFFFFFFFFFFFF;
	axis_out.tvalid = !wsf_empty;
	axis_out.tid = 0;
	
	//bready_m = 1;
end
always @(posedge clk) begin
	/*if (awvalid_m && awready_m) begin
		sc_addr <= sc_addr + (sc_len<<6);
		sc_words <= sc_words - sc_len;
	end
	/if (wvalid_m && wready_m) begin*/
	if(axis_out.tvalid && axis_out.tready) begin
		//scd_addr <= scd_addr + 64;
		scd_words <= scd_words - 1;
		
		s1_credit_add <= SCORE_RATIO/RATIO;
	end else begin
		s1_credit_add <= 0;
	end
	
	if(start) begin
	   scd_words <= sc_words_in;
	end
	
end

// Instantiations
HullFIFO #(
	.TYPE(3),
	.WIDTH(512),
	.LOG_DEPTH(6)
) wide_score_fifo (
	.clock(clk),
	.reset_n(~rst),
	.wrreq(wsf_wrreq),
	.data(wsf_din),
	.full(wsf_full),
	.rdreq(wsf_rdreq),
	.q(wsf_dout),
	.empty(wsf_empty)
);

endmodule
