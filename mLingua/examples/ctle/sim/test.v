// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit
PWLMethod pm=new;

parameter real etol = 0.005;
parameter real fp1 = 1.2e9;
parameter real fp2 = 3.4e9;
parameter real fz1 = 0.55e9;

reg in;
pwl vin;
pwl eq_out1;
pwl eq_out2;
pwl eq_out3;

initial begin
  in = 1'b0;
  `delay(100e-12) in = 1'b0;
  `delay(20e-9) in = 1'b1;
  `delay(1e-9) in = 1'b0;
  `delay(20e-9) in = 1'b0;
  $finish;
end

bit2pwl #(.vh(0.09), .vl(-0.09), .tr(3e-12) ) b2p ( .in(in), .out(vin));
ctle #(.etol(etol), .gdc(1.0), .fp1(fp1), .fp2(fp2), .fz1(fz1)) xeq1 (.in(vin), .out(eq_out1));
ctle_pfe #(.etol(etol), .gdc(1.0), .fp1(fp1), .fp2(fp2), .fz1(fz1)) xeq2 (.in(vin), .out(eq_out2));
ctle1 #(.etol(etol), .av(1.0), .fp1(fp1), .fp2(fp2), .fz1(fz1)) xeq3 (.in(vin), .out(eq_out3));

pwl_probe #(.Tstart(1e-9), .Tend(1), .filename("eq_out1.txt")) xprobe1 (.in(eq_out1));
pwl_probe #(.Tstart(1e-9), .Tend(1), .filename("eq_out2.txt")) xprobe2 (.in(eq_out2));
pwl_probe #(.Tstart(1e-9), .Tend(1), .filename("eq_out3.txt")) xprobe3 (.in(eq_out3));
pwl_probe #(.Tstart(1e-9), .Tend(1), .filename("input.txt")) xprobe0 (.in(vin));

`run_wave

endmodule
