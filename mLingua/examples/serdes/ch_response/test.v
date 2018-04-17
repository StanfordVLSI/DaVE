// test SERDES

`include "mLingua_pwl.vh"
module test;

//timeunit 1fs;
//timeprecision 1fs;
`get_timeunit

// parameters
parameter real freq = 5e9;    // pll clock frequency
parameter real TXL_Z0 = 50;   // propagation delay of TLine
parameter real TXL_TD = 0.300e-9; // propagation delay of TLine
parameter real RS = 51.0;   // termination resistance @ Tx
parameter real RT = 55.0;   // termination resistance @ Rx

// wires
wire tx_din;
real tx_out;
pwl ch_out;
pwl ch_in;
pwl tx_out1;


// a pulse
pulse #(.b0(0), .td(5e-9), .tw(0.2e-9), .tp(1)) uDIN (.out(tx_din));
//
bit2real #(.vh(1.0), .vl(-1.0)) uBtoR (.in(tx_din), .out(tx_out));
real2pwl #(.tr(20e-12)) uRtoP (.in(tx_out), .out(tx_out1));

// PHY channel
txline #(.etol(0.001), .Z0(TXL_Z0), .TD(TXL_TD), .tr(20e-12)) xtline (.rs(RS), .rt(RT), .vin(tx_out), .vout(ch_in));
channel #(.etol(0.001)) xch (.in(ch_in), .out(ch_out));

// Probe/Dump signals
pwl_probe #(.Tstart(0.1e-9), .Tend(1), .filename("ch_out.txt")) xprobe1 (.in(ch_out));
pwl_probe #(.Tstart(0.1e-9), .Tend(1), .filename("tx_out.txt")) xprobe2 (.in(tx_out1));


`run_wave

endmodule
