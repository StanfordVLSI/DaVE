// test PWL modeling
// Ramp response of CTLE model to check the error (etol) is actually bound

`include "mLingua_pwl.vh"
`define ADC_BIT 11

module test;

timeunit 1fs;
timeprecision 1fs;
`get_timeunit
PWLMethod pm=new;

// registers to hold inputs to circuit under test, wires for outputs
reg clk, rstb;
wire ready, sample, din;
wire [`ADC_BIT-1:0] dout;
wire [`ADC_BIT-1:0] dac_out;
// instance controller circuit
sar_logic c(.*);
// generate a clock with period of 20 time units
always begin
  #10;
  clk = ~clk;
end
initial clk=0;
// simulate analogue circuit with a digital model
reg [`ADC_BIT-1:0] hold;
always @(posedge sample) hold = 11'b00001000110;
assign din = ( hold >= dac_out);
// monitor some signals and provide input stimuli
initial begin
  $monitor($time, " rstb=%b ready=%b dout=%b sample=%b dac_out=%b din=%b state=%b mask=%b", rstb,ready,dout,sample,dac_out,din,c.state,c.mask);
  rstb=0;
  #100; rstb=1;
  #5000;
  $finish;
end

`run_wave

endmodule
