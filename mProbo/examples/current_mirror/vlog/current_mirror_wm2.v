// current mirror array
// Error: output current is defined as source type

module current_mirror
  (
  `input_pwl vdd,
  `input_pwl vss,
  `input_pwl iref,   // current reference		      
  input [1:0] cfg_mirr, // default 01
  `output_pwl out0, out1

);

timeunit 10ps;
timeprecision 1ps;

parameter c0 = 0.0;
parameter c1 = 0.984;
parameter c2 = -0.244;
parameter c3 = -0.494;

// Very simple functional model, will get nominal current at iCfg=1
// The model is back annotated from circuit simulation results
// the scale factor -1.0 represents the output is driven by NMOS.
pwl offset='{1.0,0.0,0.0};
pwl_add #(.no_sig(4)) xadd1 (.in('{offset,iref,iref,iref}), .scale('{1.0*c0,1.0*c1,1.0*c2*cfg_mirr[0],1.0*c3*cfg_mirr[1]}), .out(out0)); 
pwl_add #(.no_sig(4)) xadd2 (.in('{offset,iref,iref,iref}), .scale('{1.0*c0,1.0*c1,1.0*c2*cfg_mirr[0],1.0*c3*cfg_mirr[1]}), .out(out1)); 

//assign out[0] = 1.0*(c0 + c1*iref + c2*iref*cfg_mirr[0] + c3*iref*cfg_mirr[1]);
//assign out[1] = 1.0*(c0 + c1*iref + c2*iref*cfg_mirr[0] + c3*iref*cfg_mirr[1]);

endmodule 
