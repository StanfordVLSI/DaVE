// Sample-and-Hold

module tnh #(
parameter real Ch = 27.75125e-15 // hold capacitor
) (
  `input_pwl in,  // sampler voltage in
  input sclk,  // sampler clk
  //`input_pwl init_out, // virtual input to initialize out for convergence
  `output_pwl out  // sampler out
);

timeunit 1ps;
timeprecision 1ps;
`get_timeunit
PWLMethod pm=new;


// charge sharing to the input (at the beginning of track mode) is neglected
always @(sclk or `pwl_event(in)) // track mode
  if (sclk) out = in;

always @(negedge sclk) // hold mode
  out = pm.write(1.016587*pm.eval(in,`get_time), 0, `get_time);

endmodule
