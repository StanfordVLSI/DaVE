
module iintegrator(
  input pwl avdd, avss,
  input pwl iin,
  input pwl vbn,
  input rst, rstb, pwdnb,
  output pwl vout, vref, vrefi
);

timeunit 100ps;
timeprecision 100ps;
`get_timeunit
PWLMethod pm=new;

parameter Cinteg = 162e-15;

pwl xvrefi, xvref;

always @(`pwl_event(avss)) assert (avss.a == 0 && avss.b == 0) else $error("avss should be tied to 0 [V]");
always @(rst or rstb) assert (rst ^ rstb) else $error("rstb = ~ rst");

pwl_add #( .no_sig(1) ) xvrefigen ( .in('{avdd}), .scale('{0.671}), .out(xvrefi) ); 
pwl_add #( .no_sig(1) ) xvrefgen ( .in('{avdd}), .scale('{0.562}), .out(xvref) ); 
assign vrefi = pwdnb? xvrefi : avdd;
assign vref = pwdnb? xvref : avdd;

pwl_integrator_w_reset #(.etol(0.001)) xinteg (.gain(1/Cinteg), .si(iin), .reset(rst), .reset_sig(avss), .so(vout), .trigger());

endmodule
