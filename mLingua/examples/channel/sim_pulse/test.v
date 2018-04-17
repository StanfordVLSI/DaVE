// test PWL modeling


`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit
PWLMethod pm=new;

reg in;
pwl vin;
pwl vout;
real vin_r, vout_r;
integer i;

parameter real period = 400e-12;
parameter real etol = 0.005;

initial begin
  in = 1'b0;
  `delay(100e-12) in = 1'b0;
  `delay(20e-9) in = 1'b1;
  `delay(0.2e-9) in = 1'b0;
  `delay(20e-9) in = 1'b0;
  $finish;
end

bit2pwl #(.vh(1.0), .vl(0.0), .tr(3e-12) ) b2p ( .in(in), .out(vin));
channel #(.etol(etol)) xch (.in(vin), .out(vout));

pwl_probe #(.Tstart(1e-12), .Tend(1), .filename("input.txt")) xprobe1 (.in(vin));
pwl_probe #(.Tstart(1e-12), .Tend(1), .filename("ch_out.txt")) xprobe0 (.in(vout));

`run_wave

endmodule
