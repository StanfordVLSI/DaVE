// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

timeunit 1fs;
timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

parameter real freq=500e6;
parameter real infreq=21.394e6;

wire clk;
pwl vinp, vinn;
pwl voutp, voutn;
pwl vdd, vss;

vdc_pwl #(.dc(1.8)) xvdd (.vout(vdd));
vdc_pwl #(.dc(0.0)) xvss (.vout(vss));

pwl_sin #(.etol(0.001), .freq(infreq), .amp(0.15), .offset(1.2), .ph(0)) xsinp (.out(vinp));
pwl_sin #(.etol(0.001), .freq(infreq), .amp(0.15), .offset(1.2), .ph(180)) xsinn (.out(vinn));
clock #(.freq(freq), .duty(0.5), .td(1e-12)) xclk (.ckout(clk));

clk_integrating_amp dut (.*);

pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("voutp.txt")) xprobe1 (.in(voutp));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("voutn.txt")) xprobe2 (.in(voutn));
`run_wave

endmodule
