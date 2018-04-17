///////////////////////////////////////
// LUT of DC Transfer Curve
///////////////////////////////////////
parameter integer LUTSize=3;
real lx[LUTSize-1:0]; // x value
real ly[LUTSize-1:0];   // y value
real lgain[LUTSize-1:0]; // gain 

initial begin
lx[0] = -1.0; lgain[0] = 0.0; ly[0] = -0.8; 
lx[1] = -0.4; lgain[1] = 2.0; ly[1] = -0.8; 
lx[2] = 0.4; lgain[2] = 0.0; ly[2] = 0.8; 
end
///////////////////////////////////////

always @(`pwl_event(in) or wakeup) begin
  t = `get_time;              // current time
  in_value = pm.eval(in, t);  // current value
  slope = in.b;               // slope of the input

  // input changes and the current index is NOT valid
  index = find_region_limiter0(in_value);  // update index
  // evaluate the output at current time
  scale = lgain[index];            // get scale(gain) from the LUT
  out = '{ly[index]+scale*(in_value-lx[index]), scale*in.b, t}; 
  // schedule next event if necessary
  dT = calculate_dx_limiter0(in_value, slope, index); // calculate when the input will hit the inflection point and give the next index.
  if (dT >= TU) wakeup <= #(dT/TU) ~wakeup; // create next event after dT
  in_prev = in;
end
