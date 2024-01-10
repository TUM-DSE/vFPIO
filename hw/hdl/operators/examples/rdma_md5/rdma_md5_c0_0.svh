// Modified version of https://github.com/utcs-scea/amorphos-fsrf/blob/main/hw/design/md5

//
// BASE RDMA operations
//

// Tie-off
always_comb axi_ctrl.tie_off_s();

// I/O
AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

axisr_reg inst_reg_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
axisr_reg inst_reg_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));


wire                                rd_tvalid;
wire                                rd_tlast;
wire                                rd_tready;
wire [511:0]                        rd_tdata;

wire                                wr_tvalid;
wire                                wr_tready;
wire                                wr_tlast;
wire [511:0]                        wr_tdata;

// Input data stream: tready is asserted when input data queue
// is not full
assign rd_tdata  = axis_sink_int.tdata;
assign rd_tvalid = axis_sink_int.tvalid;
assign rd_tlast  = axis_sink_int.tlast;

// Output data: tlast is asserted when the hash has been computed
assign axis_src_int.tdata  = wr_tdata;
assign axis_src_int.tkeep  = 64'hffffffffffffffff;
assign axis_src_int.tid    = 0;
assign axis_src_int.tvalid = wr_tvalid;
assign axis_src_int.tlast  = wr_tlast;
assign wr_tready         = axis_src_int.tready;

// FIFO signals
wire idf_wrreq;
wire [511:0] idf_din;
wire idf_full;
wire idf_rdreq;
wire idf_valid;
wire [511:0] idf_dout;
wire idf_empty;

assign idf_wrreq = rd_tvalid;
assign idf_din   = rd_tdata;

// Can't read more data if the queue is full
assign axis_sink_int.tready = !idf_full;

quick_fifo  #(.FIFO_WIDTH(512),     // data      
			.FIFO_DEPTH_BITS(9),
			.FIFO_ALMOSTFULL_THRESHOLD(508)
	) InDataFIFO 
(
	.clk                (aclk),
	.reset_n            (aresetn),
	.din                (rd_tdata),
	.we                 (idf_wrreq),

	.re                 (idf_rdreq),
	.dout               (idf_dout),
	.empty              (idf_empty),
	.valid              (idf_valid),
	.full               (idf_full),
	.count              (),
	.almostfull         ()
);

//// MD5 core
// state and signals
reg [64:0] md5_valid;
reg [63:0] md5_words;
wire md5_in_valid = !idf_empty;
wire md5_out_valid = md5_valid[64];
wire md5_out_valid_prev;
assign md5_out_valid_prev = md5_valid[63];
reg md5_done;

reg [31:0] md5_a_reg;
reg [31:0] md5_b_reg;
reg [31:0] md5_c_reg;
reg [31:0] md5_d_reg;
wire [127:0] md5_hash;
wire [31:0] md5_a;
assign md5_a = md5_hash[31:0];
wire [31:0] md5_b;
assign md5_b = md5_hash[63:32];
wire [31:0] md5_c;
assign md5_c = md5_hash[95:64];
wire [31:0] md5_d;
assign md5_d = md5_hash[127:96];
wire [511:0] md5_chunk = idf_dout;

assign wr_tdata = md5_hash;
assign wr_tvalid = md5_done && wr_tready;
assign wr_tlast = md5_done && wr_tready;

// logic
assign idf_rdreq = 1;
always @(posedge aclk) begin
	if (~aresetn) begin
		md5_valid <= 0;
		md5_a_reg <= 0;
		md5_b_reg <= 0;
		md5_c_reg <= 0;
		md5_d_reg <= 0;
		md5_words <= 0;
		md5_done  <= 0;
	end else begin
		md5_valid <= {md5_valid[63:0], md5_in_valid};
		if (md5_out_valid) begin
			md5_a_reg <= md5_a_reg + md5_a;
			md5_b_reg <= md5_b_reg + md5_b;
			md5_c_reg <= md5_c_reg + md5_c;
			md5_d_reg <= md5_d_reg + md5_d;
			md5_words <= md5_words + 1;

			if(!md5_out_valid_prev) begin
				md5_done <= 1;
			end
		end
	end
end

// instantiation
Md5Core m (
	.clk(aclk),
	.wb(md5_chunk),
	.a0('h67452301),
	.b0('hefcdab89),
	.c0('h98badcfe),
	.d0('h10325476),
	.a64(md5_a),
	.b64(md5_b),
	.c64(md5_c),
	.d64(md5_d)
);


