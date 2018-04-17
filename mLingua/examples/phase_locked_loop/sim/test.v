// verilog simulation for pll circuit

`define vddval 1.1  // power supply value
`ifdef CKTCOMP
  `define fref 500e6  // frequency of reference clock input 
`else
  `define fref 2.0e9  // frequency of reference clock input 
`endif

`include "mLingua_pwl.vh"

module test;

//timeunit 1fs;
//timeprecision 1fs;

`get_timeunit

reg rstb;   // reset (active low)
reg refclk; // reference clock

real vdd_in;  // power supply
pwl vctrl;    // loop filter voltage in pwl datatype
wire outclk; 

// de-/assert reset
initial begin
  vdd_in = `vddval;
  rstb = 1'b0;
  #(1e-9/TU) rstb = 1'b1;
end

// generating reference clock
initial begin
refclk = 1'b0;
  forever begin
    refclk = #(0.5/`fref/TU) ~refclk;
  end
end

// save waveform if simv flag for that is on
`run_wave

parameter vinit = 0.0;
`ifdef CKTCOMP
  parameter tos = 0.0;
  parameter iup = 80e-6;
  parameter idn = 80e-6;
  parameter C1 = 31.274e-12;
  parameter C2 = 1e-12;
  parameter R = 679;
  parameter vh = 1.0;  // upper bound of vreg [V]
  parameter vl = 0.42;  // lower bound of vreg [V]
  parameter vco0 = -2.345e9; // freq offset [Hz]
  parameter vco1 = 5.825e9;   // freq gain [Hz/V]
`else
  parameter tos = 0.0;
  parameter iup = 20e-6;
  parameter idn = 20e-6;
  parameter C1 = 500e-15;
  parameter C2 = 50e-15;
  parameter R = 20e3;
  parameter vh = 1.0;  // upper bound of vreg [V]
  parameter vl = 0.0;  // lower bound of vreg [V]
  parameter vco0 = 1.5e9; // freq offset [Hz]
  parameter vco1 = 1e9;   // freq gain [Hz/V]
  //parameter jitter = 0.005; // rms jitter in (jitter/period)
  parameter jitter = 0.000; // rms jitter in (jitter/period)
`endif

// device-under-test
pll2nd #(.tos(tos), .iup(iup), .idn(idn), .R(R), .C1(C1), .C2(C2), .vh(vh), .vl(vl), .vco0(vco0), .vco1(vco1), .vinit(vinit), .jitter(jitter)) 
       xdut( .vdd_in(vdd_in), .refclk(refclk), .rstb(rstb), .outclk(outclk), .vctrl(vctrl) );

pwl_probe #(.Tstart(1e-15), .Tend(1), .filename("vctrl.txt")) xprobe0 (.in(vctrl));

`run_wave

endmodule
