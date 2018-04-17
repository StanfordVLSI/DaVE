@{
so_statevar = ['so%d' %x for x in range(1, filter_order)]
}@
////////////////////////////////////////////
// SISO Filter model using PWL approximation
////////////////////////////////////////////

/* Note Starts
  - Filter signal input port name: si
  - Filter signal output port name: so
  - Filter parameters could be either parametrizable or adjustable through ports

Ends Note */

// include files
@[for f in include_filename]
`include "@f"
@[end for]

module @(module_name)(
  @port_definition
);

timeunit @timeunit;
timeprecision @timeprec;

// DPI-C function if needed (only takes an input and produces a real output)
@[for fn in dpi_function]
import "DPI-C" pure function real @(fn)(input real x);
@[end for]

real TU;
initial $get_timeunit(TU); // timeunit in number to TU 

// PWL accuracy-related parameters
parameter etol = @etol; // error tolerance of PWL approximation

// User parameters
@[for k, v in user_param.items()]
parameter @k = @v;
@[end for]

// wires
reg wakeup;  // wake-up signal
real t0;  // time offset
real t_cur;   // current time
real dT;  // time interval of PWL waveform

int index;  // lut index
@filter_input_datatype si_at_t0;  // 
real so_cur; // current output signal value
real so_prev; // previous output signal value
real so_nxt;  // so at (t_cur+dT) for pwl output data
real so0;  // output signal value offset (so_cur at t0)
@[for x in so_statevar]
real @x;
@[end for]
@[if filter_output_datatype == 'pwl']
real so_slope; // so slope
@[end if]

// you may need some additional wire definition here

initial wakeup = 1'b0;

// @@si_sensitivity is just "si" if it is piecewise constant waveform
// otheriwse, it is "si.t0 or si.s0 or si.slope"
always @@(@(si_sensitivity) or wakeup) begin
  t_cur = $realtime*TU;
  so_cur = fn_@(module_name)(index, si_at_t0, so0 @so_derivative @fn_input);

  // you may need some additional code here

@[if filter_input_datatype == 'real']  
  if (si != si_at_t0) begin 
@[end if]
@[if filter_input_datatype == 'pwl']  
  if (si.a != si_at_t0.a || si.b != si_at_t0.b) begin 
@[end if]
    t0 = t_cur;
    so0 = so_cur;
@[for x in range(1, filter_order)] 
    so@x = fn_@(x)_derivative_@(module_name)(t_cur-t0, si_at_t0, so0 @so_derivative @fn_input); 
@[end for]
    si_at_t0 = si;

    // you may need some additional code here
  end

  dT = calculate_Tintv_@(module_name)(etol, t_cur-t0, si_at_t0, so0 @so_derivative @fn_input);
  so_nxt = fn_@(module_name)(t_cur-t0+dT, si_at_t0, so0 @so_derivative @fn_input);
@[if filter_output_datatype == 'real']
  so = so_cur;
@[end if]
@[if filter_output_datatype == 'pwl']
  so_slope = (so_nxt-so_cur)/dT;
  so = '{t_cur, so_cur, so_slope};
@[end if]
  so_prev = so_cur;

  // you may need some additional code here 
  // e.g. adjust dT

  // don't trigger event if dT > @tmax
  if (dT <= @tmax) wakeup <= #(dT/TU) ~wakeup;
  index = index + 1;
end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_@(module_name);
input int index; 
input @filter_input_datatype si; 
input real so0 @so_derivative @fn_input;
begin
  return @response_function;
end
endfunction

@(derivative_functions)

endmodule
