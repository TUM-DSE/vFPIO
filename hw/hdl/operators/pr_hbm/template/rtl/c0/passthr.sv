import lynxTypes::*;

module passthr (
    input  logic            aclk,
    input  logic            aresetn,

    AXI4SR.s                 axis_in,
    AXI4SR.m                 axis_out
);

always_comb begin
    axis_out.tvalid = axis_in.tvalid;
    axis_out.tkeep  = axis_in.tkeep;
    axis_out.tid    = axis_in.tid;
    axis_out.tlast  = axis_in.tlast;
    axis_out.tdata  = axis_in.tdata;

    axis_in.tready  = axis_out.tready;
end

endmodule
