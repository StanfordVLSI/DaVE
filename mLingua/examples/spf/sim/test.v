// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

timeunit 1ps;
timeprecision 1ps;
`get_timeunit
PWLMethod pm=new;

reg in;
pwl vin;
pwl vout;

initial begin
  in = 1'b0;
  `delay(1e-12) in = 1'b1;
  `delay(100e-12) in = 1'b0;
  `delay(20e-9) in = 1'b1;
  `delay(21e-9);
end

bit2pwl #(.vh(0.1), .vl(-0.1), .tr(40e-12) ) b2p ( .in(in), .out(vin));
pwl_spf #(.etol(0.001), .w1(2*`M_PI*500e6)) xeq (.in(vin), .out(vout));

pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("output.txt")) xprobe0 (.in(vout));
pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("input.txt")) xprobe1 (.in(vin));

`run_wave

endmodule
