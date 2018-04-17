/* *****************************************************************************
 *  * A continuous-time comparator
 *   * ****************************************************************************/

module comparator #(
  parameter real offset=0.0, // input voltage offset
  parameter real etol=1e-4,  // error tolerance of a filter model
  parameter real w3db=`M_TWO_PI*1e9 // comparator bandwidth
) (
`input_pwl vdd,

`input_pwl inp,
`input_pwl inn,

input [4:0] cfg_offset_p,
input [4:0] cfg_offset_n,

output reg out
);

timeunit 1ps;
timeprecision 1ps;
`get_timeunit
PWLMethod pm=new;

real t0;
real offset_p, offset_n;

wire [4:0] cfg_offset_n_reverse;

assign cfg_offset_n_reverse = {<<{cfg_offset_n}};

always @(cfg_offset_p) begin
  offset_p = cfg_offset_p*1.0e-3;
end
always @(cfg_offset_n_reverse) begin
  offset_n = cfg_offset_n_reverse*1.0e-3;
end

always @(`pwl_event(inp) or `pwl_event(inn) or offset_p or offset_n) begin
  t0 = `get_time;
  if ( (pm.eval(inp,t0)-pm.eval(inn,t0)+offset_p-offset_n) >=0 ) out = 1'b1;
  else out = 1'b0;
end

endmodule

