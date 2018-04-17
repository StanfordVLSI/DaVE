// test SERDES

`include "mLingua_pwl.vh"
module test;

`get_timeunit

// parameters
parameter real freq = 5e9;    // pll clock frequency
parameter real TXL_Z0 = 50;   // propagation delay of TLine
parameter real TXL_TD = 0.300e-9; // propagation delay of TLine
parameter real RS = 51.0;   // termination resistance @ Tx
parameter real RT = 55.0;   // termination resistance @ Rx

// wires
wire clk, rstb, tx_in;
wire rx_out, rx_clk, rx_clkb;
pwl ch_out, eq_out, dfe_out, vctrl;
pwl ch_in;
real tx_out;
real ch_out_r, eq_out_r, dfe_out_r, vctrl_r;

assign rx_clkb = ~rx_clk;

// TX reference clock, reset generation
pulse #(.td(1e-12), .tw(1), .tp(2)) xrstgen (.out(rstb));
clock #(.freq(freq)) xclkgen (.ckout(clk));

// TX PLL, PRBS generator, Driver w/ Pre-Emphasis
pll2nd #(.tos(0), .iup(20e-6), .idn(20e-6), .R(20e3), .C1(500e-15), .C2(50e-15), .vh(1.0), .vl(0.0), .vco0(4.5e9), .vco1(1.0e9), .vinit(0.45), .jitter(0.005)) tx_pll( .vdd_in(1.0), .refclk(clk), .rstb(rstb), .outclk(tx_clk), .vctrl(vctrl) );

prbs21 prbs (.clk(tx_clk), .out(tx_in));
tx_driver_real #(.amp(2.0), .wtap1(0.90),.wtap0(-0.10)) txdrv (.in(tx_in), .clk(tx_clk), .out(tx_out));

// PHY channel
txline #(.etol(0.001), .Z0(TXL_Z0), .TD(TXL_TD), .tr(20e-12)) xtline (.rs(RS), .rt(RT), .vin(tx_out), .vout(ch_in));
channel #(.etol(0.01)) xch (.in(ch_in), .out(ch_out));

// RX EQ+DFE, Bang-Bang CDR
ctle #(.etol(0.01), .gdc(1.0), .fp1(1.2e9), .fp2(3.4e9), .fz1(0.55e9)) xeq (.in(ch_out), .out(eq_out));
dfe #(.tr(20e-12), .dc(0), .amp(1), .wtap0(-0.13), .wtap1(-0.025)) xdfe(.in(eq_out), .data(rx_out), .clk(rx_clkb), .out(dfe_out));
bb_cdr #(.vth(0), .dco_Nbit(20), .init_dctrl({1'b1,19'b0}), .Kp(256), .Ki(1), .freq_min(4.0e9), .freq_max(6.0e9)) xcdr(.in(dfe_out), .clk(rx_clk), .data(rx_out)); // use center value of init_dctrl for faster start-up

// Probe/Dump signals
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("ch_out.txt")) xprobe1 (.in(ch_out));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("eq_out.txt")) xprobe2 (.in(eq_out));
pwl_probe #(.Tstart(1e-6), .Tend(1), .filename("dfe_out.txt")) xprobe3 (.in(dfe_out));

`run_wave

endmodule
