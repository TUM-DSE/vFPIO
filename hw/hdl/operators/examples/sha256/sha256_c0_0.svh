// Modified version of https://github.com/utcs-scea/amorphos-fsrf/tree/main/hw/design/sha

AXI4SR axis_sink_int ();
AXI4SR axis_src_int ();

`ifdef EN_STRM
    `ifdef EN_MEM
        axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_switch_mem_0_sink), .m_axis(axis_sink_int));
        axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_switch_mem_0_src));
    `else
		axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_host_0_sink), .m_axis(axis_sink_int));
        axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_host_0_src));
    `endif
`else
axisr_reg_rtl inst_reg_slice_sink (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_card_0_sink), .m_axis(axis_sink_int));
axisr_reg_rtl inst_reg_slice_src (.aclk(aclk), .aresetn(aresetn), .s_axis(axis_src_int), .m_axis(axis_card_0_src));
`endif

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

//// SHA256 core
// state and signals
reg [63:0] sha_words;
reg [64:0] sha_valid;
wire sha_in_valid;
assign sha_in_valid = idf_valid;
wire sha_out_valid;
assign sha_out_valid = sha_valid[64];
wire sha_out_valid_prev;
assign sha_out_valid_prev = sha_valid[63];
reg sha_done;
// reg sha_done_temp;

reg [31:0] sha_a_reg;
reg [31:0] sha_b_reg;
reg [31:0] sha_c_reg;
reg [31:0] sha_d_reg;
reg [31:0] sha_e_reg;
reg [31:0] sha_f_reg;
reg [31:0] sha_g_reg;
reg [31:0] sha_h_reg;
wire [255:0] sha_hash;
wire [31:0] sha_a;
assign sha_a = sha_hash[31:0];
wire [31:0] sha_b;
assign sha_b = sha_hash[63:32];
wire [31:0] sha_c;
assign sha_c = sha_hash[95:64];
wire [31:0] sha_d;
assign sha_d = sha_hash[127:96];
wire [31:0] sha_e;
assign sha_e = sha_hash[159:128];
wire [31:0] sha_f;
assign sha_f = sha_hash[191:160];
wire [31:0] sha_g;
assign sha_g = sha_hash[223:192];
wire [31:0] sha_h;
assign sha_h = sha_hash[255:224];
wire [511:0] sha_chunk = idf_dout;

// Output data is valid only if core is done and  wr_tready is high
wire [255:0] sha_out;
assign sha_out = {sha_h_reg, sha_g_reg, sha_f_reg, sha_e_reg, sha_d_reg, sha_c_reg, sha_b_reg, sha_a_reg};
assign wr_tdata = sha_out;
assign wr_tvalid = sha_done && wr_tready;
assign wr_tlast = sha_done && wr_tready;

// logic
assign idf_rdreq = 1;
always @(posedge aclk) begin
	if (~aresetn) begin
		sha_valid <= 0;
		sha_words <= 0;
		sha_done <= 0;
		// sha_done_temp <= 0;
		sha_a_reg <= 0;
		sha_b_reg <= 0;
		sha_c_reg <= 0;
		sha_d_reg <= 0;
		sha_e_reg <= 0;
		sha_f_reg <= 0;
		sha_g_reg <= 0;
		sha_h_reg <= 0;
	end
	else begin
		sha_valid <= {sha_valid[63:0], sha_in_valid};
		if (sha_out_valid) begin
			sha_a_reg <= sha_a_reg + sha_a;
			sha_b_reg <= sha_b_reg + sha_b;
			sha_c_reg <= sha_c_reg + sha_c;
			sha_d_reg <= sha_d_reg + sha_d;
			sha_e_reg <= sha_e_reg + sha_e;
			sha_f_reg <= sha_f_reg + sha_f;
			sha_g_reg <= sha_g_reg + sha_g;
			sha_h_reg <= sha_h_reg + sha_h;
			sha_words <= sha_words + 1;

			if(!sha_out_valid_prev) begin
				sha_done <= 1;
			end
		end
		// if(sha_done_temp) begin
		//     sha_done <= 1;
		// end
	end
end

// instantiation
sha256_transform #(
	.LOOP(1)
) sha (
	.clk(aclk),
	.rst_n(aresetn),
	.feedback(0),
	.cnt(0),
	.rx_state(256'h5be0cd191f83d9ab9b05688c510e527fa54ff53a3c6ef372bb67ae856a09e667),
	.rx_input(sha_chunk),
	.tx_hash(sha_hash)
);

//////////////////////////////////////////////////////////////////////////////////////////////////////
//---------------------------------log file print--------------------------------------------------//
////////////////////////////////////////////////////////////////////////////////////////////////////
// `define LOG_NULL
// `ifdef LOG_FILE
int file;

initial begin
	file = $fopen("/scratch/harshanavkis/fair-proj/Coyote/sha256_sim_build/sha256_log.txt","w");
	if(file) 
		$display("sha256_log file open successfully\n");
	else 
		$display("Failed to open sha256_log file\n");	
end

// Dump
// initial begin
//     $dumpfile("sha256-dump.vcd"); $dumpall;
// end

always @ (posedge aclk) begin
	$display("******Start clock log******");
	$display("sha_done: %x", sha_done);
	$display("sha_chunk: %x", sha_chunk);
	$display("wr_tdata: %x", wr_tdata);
	$display("sha_valid: %x", sha_valid);
	$display("sha_in_valid: %x", sha_in_valid);
	$display("sha_out_valid: %x", sha_out_valid);
	$display("sha_a_reg: %x", sha_a_reg);
	$display("sha_b_reg: %x", sha_b_reg);
	$display("sha_c_reg: %x", sha_c_reg);
	$display("sha_d_reg: %x", sha_d_reg);
	$display("sha_e_reg: %x", sha_e_reg);
	$display("sha_f_reg: %x", sha_f_reg);
	$display("sha_g_reg: %x", sha_g_reg);
	$display("sha_h_reg: %x", sha_h_reg);
	$display("sha_a: %x", sha_a);
	$display("sha_b: %x", sha_b);
	$display("sha_c: %x", sha_c);
	$display("sha_d: %x", sha_d);
	$display("sha_e: %x", sha_e);
	$display("sha_f: %x", sha_f);
	$display("sha_g: %x", sha_g);
	$display("sha_h: %x", sha_h);
	$fwrite(file, "sha_out: %x", sha_out);
	$fwrite(file, "\n");
	$display("******End clock log******");
end
// `endif
////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////
