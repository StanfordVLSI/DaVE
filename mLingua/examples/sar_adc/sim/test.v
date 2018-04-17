// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"
`include "sar_adc_def.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit
PWLMethod pm=new;

parameter real freq=20e6;
parameter real infreq=0.021394e6;

wire clk;
wire [`ADC_BIT-1:0] dout;
pwl vinp, vinn;
pwl vcm;
pwl vdd, vss;
pwl ibiasn;
pwl vrefp, vrefn;

vdc #(.dc(1.8)) xvdd (.vout(vdd));
vdc #(.dc(0.0)) xvss (.vout(vss));
vdc #(.dc(1.6)) xvrefp (.vout(vrefp));
vdc #(.dc(0.8)) xvrefn (.vout(vrefn));
vdc #(.dc(1.2)) xvcm (.vout(vcm));
idc #(.dc(20e-6), .is_n(1'b1)) xibiasn (.refnode(vdd), .outnode(ibiasn));

pwl_sin #(.etol(0.00001), .freq(infreq), .amp(0.180), .offset(1.2), .ph(0)) xsinp (.out(vinp));
pwl_sin #(.etol(0.00001), .freq(infreq), .amp(0.180), .offset(1.2), .ph(180)) xsinn (.out(vinn));
clock #(.freq(freq), .duty(0.5), .td(1e-12)) xclk (.ckout(clk));
pulse #(.b0(1'b0), .td(20e-9), .tw(1), .tp(2)) xpulse(.out(rstb));

sar_adc dut (.vdd(vdd), .vss(vss), .clk(clk), .rstb(rstb), .vinp(vinp), .vinn(vinn), .vcm(vcm), .vrefp(vrefp), .vrefn(vrefn), .ibiasn(ibiasn), .dout(dout), .ready());

`run_wave

endmodule
