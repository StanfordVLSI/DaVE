// test SERDES

`include "mLingua_pwl.vh"
module test;

//timeunit 1fs;
//timeprecision 1fs;
`get_timeunit

// parameters
parameter real freq = 5e9;

// wires
wire clk, rstb, tx_in;
wire rx_out, rx_clk, rx_clkb;
pwl tx_out, ch_out, eq_out, dfe_out, vctrl;
real tx_out_r, ch_out_r, eq_out_r, dfe_out_r, vctrl_r;

assign rx_clkb = ~rx_clk;

// TX reference clock, reset generation
pulse #(.td(1e-12), .tw(1), .tp(2)) xrstgen (.out(rstb));
clock #(.freq(freq)) xclkgen (.ckout(clk));

// TX PLL, PRBS generator, Driver w/ Pre-Emphasis
pll2nd `protect
//pragma protect 
//pragma protect begin
#(.tos(0), .iup(20e-6), .idn(20e-6), .R(20e3), .C1(500e-15), .C2(50e-15), .vh(1.0), .vl(0.0), .vco0(4.5e9), .vco1(1.0e9), .vinit(0.45), .jitter(0.005)) 
//pragma protect end
`endprotect tx_pll( .vdd_in(1.0), .refclk(clk), .rstb(rstb), .outclk(tx_clk), .vctrl(vctrl) );

prbs7 prbs (.clk(tx_clk), .out(tx_in));
tx_driver_real `protect
//pragma protect 
//pragma protect begin
//#(.tr(20e-12), .ntap(2), .wtap('{0.90,-0.10})) 
//#(.tr(1e-12), .wtap1(0.90),.wtap0(-0.10)) 
#(.amp(2.0), .wtap1(0.90),.wtap0(-0.10)) 
//pragma protect end
`endprotect txdrv (.in(tx_in), .clk(tx_clk), .out(tx_out_r));
real2pwl #(.tr(20e-12)) uR2PTXOUT (.in(tx_out_r), .out(tx_out));

// PHY channel
channel #(.etol(0.01)) xch (.in(tx_out), .out(ch_out));

// RX EQ+DFE, Bang-Bang CDR
ctle `protect
//pragma protect 
//pragma protect begin
#(.etol(0.01), .gdc(1.0), .fp1(1.2e9), .fp2(3.4e9), .fz1(0.55e9)) 
//pragma protect end
`endprotect xeq (.in(ch_out), .out(eq_out));
dfe `protect
//pragma protect 
//pragma protect begin
//#(.tr(20e-12), .dc(0), .amp(1), .ntap(2), .wtap('{-0.025,-0.13})) 
#(.tr(20e-12), .dc(0), .amp(1), .wtap0(-0.13), .wtap1(-0.025))
//pragma protect end
`endprotect xdfe(.in(eq_out), .data(rx_out), .clk(rx_clkb), .out(dfe_out));
bb_cdr `protect
//pragma protect 
//pragma protect begin
#(.vth(0), .dco_Nbit(14), .init_dctrl(14'b10_0000_0000_0000), .Kp(256), .Ki(1), .Nd(4), .freq_min(4.5e9), .freq_max(5.5e9), .init_phase(0)) 
//pragma protect end
`endprotect xcdr(.in(dfe_out), .clk(rx_clk), .data(rx_out));

// Probe/Dump signals
pwl rx_clk_pwl;
bit2pwl #(.tr(10e-12), .tf(10e-12), .vh(0.4), .vl(-0.4)) ib2p (.in(rx_clk), .out(rx_clk_pwl));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("ch_out.txt")) xprobe1 (.in(ch_out));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("eq_out.txt")) xprobe2 (.in(eq_out));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("dfe_out.txt")) xprobe3 (.in(dfe_out));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("rxclk_out.txt")) xprobe4 (.in(rx_clk_pwl));
/*
*/


`run_wave

endmodule
