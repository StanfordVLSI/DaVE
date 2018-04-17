/////////////////////////////////////
// Simple Phase domain model of a VCO
/////////////////////////////////////

module ringosc (
  input pwl vdd,  
  input pwl vreg, // PWL sig
  output cko,
  output ckob
);


timeunit 1fs;
timeprecision 1fs;
`get_timeunit

parameter vh = 0.9;  // upper bound of vreg [V]
parameter vl = 0.4;  // lower bound of vreg [V]
parameter vco0 = -2.863e9; // freq offset [Hz]
parameter vco1 = 6.70e9;   // freq gain [Hz/V]
parameter jitter = 0.000; // rms jitter in (jitter/period)

pwl freq, phase;

assign ckob = ~cko;

txf_vco #(.vh(vh), .vl(vl), .vco0(vco0), .vco1(vco1)) xdc (.in(vreg), .out(freq));
pwl_integrator #(.etol(0.01), .modulo(0.5), .noise(jitter)) xph2clk(.gain(1.0), .si(freq), .so(phase), .trigger(cko));

endmodule
