// test PWL modeling


`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit
PWLMethod pm=new;

reg clk;
wire in;
pwl vin;
pwl vout;
real vin_r, vout_r;
integer i;

parameter real period = 400e-12;
parameter real etol = 0.001;

initial begin
  clk = 1'b0;
  forever begin
    clk = `delay(period/2) ~clk;
  end
  $finish;
end

prbs7 prbs (.clk(clk), .out(in));
bit2pwl #(.vh(0.1), .vl(-0.1), .tr(5e-12) ) b2p ( .in(in), .out(vin));
channel #(.etol(etol)) xch (.in(vin), .out(vout));

pwl_probe #(.Tstart(1e-12), .Tend(1), .filename("input.txt")) xprobe1 (.in(vin));
pwl_probe #(.Tstart(1e-12), .Tend(1), .filename("ch_out.txt")) xprobe0 (.in(vout));

`run_wave

endmodule
