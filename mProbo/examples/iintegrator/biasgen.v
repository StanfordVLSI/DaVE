// bias circuit for opamp & comparator

/* Note
  1. In the real circuit, 'vbn' is a voltage signal but it is a current signal in this behavioral model.
*/

module biasgen #(
  parameter wakeup_delay = 10e-9 // wakeup delay from power down
) (
  input pwl avdd, avss,
  input pwdn,
  output pwl vbn 
);

timeunit 100ps;
timeprecision 100ps;
`get_timeunit


reg pwdn_dly=1'b1;

always @(pwdn) pwdn_dly <= `delay(wakeup_delay) pwdn;

always @(pwdn_dly or `pwl_event(avdd)) begin
  if (!pwdn_dly) vbn = '{-58.88e-6 + 46.91e-6*avdd.a,  46.91e-6*avdd.b, `get_time};
  else vbn = '{0,0,0}; // power down
end

endmodule
