// test module

`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit // TU = timeunit of this module

parameter period = 10e-6;
parameter tr = 0.01e-6;
parameter real etol=0.01;

PWLMethod pm=new;

pwl inp;
pwl inm;
pwl vout; 
pwl vddh = '{3.6,0,0};
pwl ib = '{15e-6,0,0};
real vout_r, inm_r, inp_r;

reg pulse;
initial begin
  pulse = 1'b1;
  #(400e-9/TU);
  pulse = 1'b0;
  for (int i=0;i<1000000;i++) pulse = #(period/TU/2.0) ~pulse;
end

assign inm = vout;
bit2pwl #(.vh(2.50), .vl(1.40), .tr(tr)) b2p (.in(pulse), .out(inp));
iamp #(.etol(etol)) dut( .ib(ib), .inp(inp), .inm(inm), .vdda(vddh), .out(vout));
pwl_probe #(.Tstart(1e-9), .Tend(1), .filename("inm.txt")) xprobe1 (.in(inm));

`run_wave

endmodule
