// analog mux

// wrong model:
// sel0 is inverted or two analog inputs are swapped.

module amux(
  `input_pwl avdd, avss,
  `input_pwl i0, i1,
  input sel0,
  `output_pwl out
);

timeunit 100ps;
timeprecision 100ps;

always @(sel0 or `pwl_event(i0) or `pwl_event(i1)) out = sel0? i1 : i0;

endmodule
