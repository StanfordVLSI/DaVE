// analog mux

module amux(
  `input_pwl avdd, avss,
  `input_pwl i0, i1,
  input sel0,
  `output_pwl out
);

timeunit 100ps;
timeprecision 100ps;

always @(sel0 or `pwl_event(i0) or `pwl_event(i1)) out = sel0? i0 : i1;

endmodule
