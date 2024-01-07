`timescale 1ns / 1ps


module rng_axis_wrapper
(
    input aclk,
    input aresetn,
    
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
);
	
    reg ul_resetn;
    reg init;
    reg input_complete;
    reg rng_start;
    reg [63:0] size_shift_in;
    reg [63:0] linear_in;
    reg [63:0] read_in;


    logic [15 : 0] axi_awid;
    logic [17 : 0] axi_awaddr;
    logic [7 : 0]  axi_awlen;
    logic [2 : 0]  axi_awsize;
    logic axi_awvalid;
    logic axi_awready;

    logic [511 : 0] axi_wdata;
    logic [63 : 0] axi_wstrb;
    logic axi_wlast;
    logic axi_wvalid;
    logic axi_wready;

    logic [15 : 0] axi_arid;
    logic [17 : 0] axi_araddr;
    logic [7 : 0] axi_arlen;
    logic [2 : 0] axi_arsize;

    logic [15 : 0] axi_rid;
    logic [511 : 0] axi_rdata;
    logic [1 : 0] axi_rresp;
    logic axi_rlast;
    logic axi_rvalid;
    logic axi_rready;

    axi_bram_ctrl_0 axi_bram (
        .s_axi_aclk(aclk),        // input wire s_axi_aclk
        .s_axi_aresetn(aresetn && ul_resetn),  // input wire s_axi_aresetn
        .s_axi_awid(axi_awid),        // input wire [15 : 0] s_axi_awid
        .s_axi_awaddr(axi_awaddr),    // input wire [21 : 0] s_axi_awaddr
        .s_axi_awlen(axi_awlen),      // input wire [7 : 0] s_axi_awlen
        .s_axi_awsize(axi_awsize),    // input wire [2 : 0] s_axi_awsize
        .s_axi_awburst(2'b01/*axi_awburst*/),  // input wire [1 : 0] s_axi_awburst
        .s_axi_awlock(1'b0/*axi_awlock*/),    // input wire s_axi_awlock
        .s_axi_awcache(4'b0/*axi_awcache*/),  // input wire [3 : 0] s_axi_awcache
        .s_axi_awprot(3'b0/*axi_awprot*/),    // input wire [2 : 0] s_axi_awprot
        .s_axi_awvalid(axi_awvalid),  // input wire s_axi_awvalid
        .s_axi_awready(axi_awready),  // output wire s_axi_awready
        .s_axi_wdata(axi_wdata),      // input wire [511 : 0] s_axi_wdata
        .s_axi_wstrb(axi_wstrb),      // input wire [63 : 0] s_axi_wstrb
        .s_axi_wlast(axi_wlast),      // input wire s_axi_wlast
        .s_axi_wvalid(axi_wvalid),    // input wire s_axi_wvalid
        .s_axi_wready(axi_wready),    // output wire s_axi_wready
        //.s_axi_bid(axi_bid),          // output wire [15 : 0] s_axi_bid
        //.s_axi_bresp(axi_bresp),      // output wire [1 : 0] s_axi_bresp
        //.s_axi_bvalid(axi_bvalid),    // output wire s_axi_bvalid
        .s_axi_bready(1'b1/*axi_bready*/),    // input wire s_axi_bready
        .s_axi_arid(axi_arid),        // input wire [15 : 0] s_axi_arid
        .s_axi_araddr(axi_araddr),    // input wire [21 : 0] s_axi_araddr
        .s_axi_arlen(axi_arlen),      // input wire [7 : 0] s_axi_arlen
        .s_axi_arsize(axi_arsize),    // input wire [2 : 0] s_axi_arsize
        .s_axi_arburst(2'b01/*axi_arburst*/),  // input wire [1 : 0] s_axi_arburst
        .s_axi_arlock(1'b0/*axi_arlock*/),    // input wire s_axi_arlock
        .s_axi_arcache(4'b0/*axi_arcache*/),  // input wire [3 : 0] s_axi_arcache
        .s_axi_arprot(3'b0/*axi_arprot*/),    // input wire [2 : 0] s_axi_arprot
        .s_axi_arvalid(axi_arvalid),  // input wire s_axi_arvalid
        .s_axi_arready(axi_arready),  // output wire s_axi_arready
        .s_axi_rid(axi_rid),          // output wire [15 : 0] s_axi_rid
        .s_axi_rdata(axi_rdata),      // output wire [511 : 0] s_axi_rdata
        .s_axi_rresp(axi_rresp),      // output wire [1 : 0] s_axi_rresp
        .s_axi_rlast(axi_rlast),      // output wire s_axi_rlast
        .s_axi_rvalid(axi_rvalid),    // output wire s_axi_rvalid
        .s_axi_rready(axi_rready)    // input wire s_axi_rready
    ); 

	rng_top_axis rt (
		.clk(aclk),
		.rst(~aresetn || ~ul_resetn),
		
		.arid_m(axi_arid),
		.araddr_m(axi_araddr),
		.arlen_m(axi_arlen),
		.arsize_m(axi_arsize),
		.arvalid_m(axi_arvalid),
		.arready_m(axi_arready),
		
		.rid_m(axi_rid),
		.rdata_m(axi_rdata),
		.rresp_m(axi_rresp),
		.rlast_m(axi_rlast),
		.rvalid_m(axi_rvalid),
		.rready_m(axi_rready),
		
		// .awid_m(axi_m.awid),
		// .awaddr_m(axi_m.awaddr),
		// .awlen_m(axi_m.awlen),
		// .awsize_m(axi_m.awsize),
		// .awvalid_m(axi_m.awvalid),
		// .awready_m(axi_m.awready),
		
		// .wdata_m(axi_m.wdata),
		// .wstrb_m(axi_m.wstrb),
		// .wlast_m(axi_m.wlast),
		// .wvalid_m(axi_m.wvalid),
		// .wready_m(axi_m.wready),
		
		// .bid_m(axi_m.bid),
		// .bresp_m(axi_m.bresp),
		// .bvalid_m(axi_m.bvalid),
		// .bready_m(axi_m.bready),
		
		// .softreg_req_valid(softreg_req.valid),
		// .softreg_req_isWrite(softreg_req.isWrite),
		// .softreg_req_addr(softreg_req.addr),
		// .softreg_req_data(softreg_req.data),
		
		// .softreg_resp_valid(softreg_resp.valid),
		// .softreg_resp_data(softreg_resp.data)
        .size_shift_in(size_shift_in),
        .linear_in(linear_in),
        .read_in(read_in),
        .rng_start(rng_start),

        .axis_out(axis_out)
	);

always_comb begin
  axi_wdata = axis_in.tdata;
  axi_wstrb = 64'hffffffffffffffff;
  axi_wvalid = axis_in.tvalid && init;
  axi_wlast = 1;

  axis_in.tready = (axi_wready || ~init) && ~input_complete && aresetn && ul_resetn;
end

always @(posedge aclk) begin
  
  if(~aresetn || ~ul_resetn) begin

    init <= 0;
    rng_start <= 0;
    input_complete <= 0; 
    axi_awaddr <= 0;
    axi_awvalid <= 0;
    ul_resetn <= 1;

  end else begin
    
    //first word contains meta data
    if(axis_in.tvalid && axis_in.tready && ~init) begin
      init <= 1;
      axi_awaddr <= 0;
      axi_awvalid <= 1;
      axi_awid <= 0;
      axi_awlen <= 0;
      axi_awsize <= 0;

      size_shift_in <= axis_in.tdata[0+:64];
      linear_in <= axis_in.tdata[64+:64];
      read_in <= axis_in.tdata[128+:64];
    end

    // //increment address
    // if(axi_awvalid && axi_awready) begin
    //   if(axi_awaddr+64< (1 << (19 + 6 + size_shift_in)))
    //     axi_awaddr <= axi_awaddr + 64;
    //   else
    //     axi_awvalid <= 0;
    // end

    //input complete
    rng_start <= 0;
    if(axis_in.tvalid && axis_in.tready && axis_in.tlast) begin
      input_complete <= 1;
      rng_start <= 1;
    end
    
    //output complete
    if(axis_out.tvalid && axis_out.tready && axis_out.tlast)
      ul_resetn <= 0;
      
  end
end

endmodule
