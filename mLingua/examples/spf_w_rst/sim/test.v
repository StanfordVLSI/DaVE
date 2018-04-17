// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

reg in;
reg reset;
pwl reset_sig;
pwl vin;
pwl vout;

initial begin
  reset = 1'b0;
  in = 1'b0;
  reset_sig = pm.write(0.5,0,0);
  `delay(1e-12) in = 1'b1;
  `delay(100e-12) in = 1'b0;
  `delay(20e-9) in = 1'b1;
  `delay(21e-9);
  reset = 1'b1;
  `delay(500e-9);
  reset = 1'b0;
  `delay(500e-9);
end

bit2pwl #(.vh(0.1), .vl(-0.1), .tr(40e-12) ) b2p ( .in(in), .out(vin));
//pwl_spf #(.etol(0.001), .w1(2*`M_PI*500e6), .wrst(2*`M_PI*10e6)) xeq (.reset(reset), .in(vin), .reset_sig(reset_sig), .out(vout));
pwl_filter_real_w_reset #(.etol(0.001), .filter(0)) dut (.reset(reset), .in(vin), .in_rst(reset_sig), .out(vout), .fp1(500e6), .fp_rst(10e6));

`run_wave

endmodule
