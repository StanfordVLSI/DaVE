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

`get_timeunit // get timeunit in sec and assign it to the variable 'TU'

// Method for PWL signal processing
PWLMethod pm=new;

// PWL accuracy-related parameters
parameter etol = @etol; // error tolerance of PWL approximation

// User parameters
@[for k, v in user_param.items()]
parameter @k = @v;
@[end for]

// wires
event wakeup;  // event signal
real t0;  // time offset
real t_cur;   // current time
real dTr;  // time interval of PWL waveform
int dT=1;
int dTm, t_prev;
reg event_in=1'b0;

@filter_input_datatype si_at_t0;  // 
real so_cur; // current output signal value
real so_prev; // previous output signal value
real so_nxt;  // so at (t_cur+dT) for pwl output data
real yo0;  // output signal value offset (so_cur at t0)
real yo1;  // first derivative y'(0)
real xi0;  // initial state of input
real xi1;  // initial state of first derivative of input
@[for x in so_statevar]
real @x;
@[end for]
@[if filter_output_datatype == 'pwl']real so_slope; // so slope
@[end if]
@[for k, v in other_input.items()]@[if v=='pwl']real @(k+'_s'); // sampled version of @(k) when input si changes
@[end if]@[end for]

// you may need some additional wire definition here

// @@si_sensitivity is just "si" if it is piecewise constant waveform
// otheriwse, it is "si.t0 or si.s0 or si.slope"

always @@(@(si_sensitivity) or wakeup) begin
  dTm = $realtime - t_prev;
  @[if filter_input_datatype == 'real']  
    event_in = si != si_at_t0;
  @[elif filter_input_datatype == 'pwl']  
    event_in = `pwl_check_diff(si, si_at_t0);
  @[end if]
  if (((dT==dTm)&&(dTm>=1)) || event_in) begin
    t_prev = $realtime;
    t_cur = `get_time;
  @[for k, v in other_input.items()] @[if v=='pwl'] @(k+'_s') = pm.eval(@(k), t_cur); // sampled version of @(k)
  @[end if]@[end for]
      //so_cur = fn_@(module_name)(t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1 @so_derivative @fn_input_s);
      so_cur = so.a + so.b*(t_cur-so.t0);
      // you may need some additional code here
    
      if (event_in) begin 
        yo0 = so_cur;
        yo1 = so.b;
    @[if filter_input_datatype == 'real']  
        xi0 = si;
    @[elif filter_input_datatype == 'pwl']  
        xi0 = si.a;
        xi1 = si.b;
    @[end if]
  @#  @[for x in range(1, filter_order)] 
  @#      so@x = fn_@(x)_derivative_@(module_name)(t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1 @so_derivative @fn_input_s); 
  @#  @[end for]
        //yo1 = fn_1_derivative_@(module_name)(t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1 @fn_input_s); 
        si_at_t0 = si;
        t0 = t_cur;
    
        // you may need some additional code here
      end
    
      dTr = calculate_Tintv_@(module_name)(etol, t_cur-t0, si_at_t0, xi0, xi1, yo0, yo1 @so_derivative @fn_input_s);
      dTr = max(dTr,1);
      //dTr = time'(dTr/TU)*TU;
      if (dT>0) begin
        dT = time'(dTr/TU);
        so_nxt = fn_@(module_name)(t_cur-t0+dTr, si_at_t0, xi0, xi1, yo0, yo1 @so_derivative @fn_input_s);
        //if (abs(so_nxt-so_cur)>etol) begin
          so_slope = (so_nxt-so_cur)/dTr;
          so = '{so_cur, so_slope, t_cur};
          ->> #(dT) wakeup;
        //end
        //else so = '{fn_@(module_name)(1/0, si_at_t0, xi0, xi1, yo0, yo1 @so_derivative @fn_input_s),0,t_cur};
      end
      //else 
      //  so = '{so_cur+so.b*dTr, 0, t_cur};
    // you may need some additional code here 
  end

end

/*******************************************
  Response function, its 1st/2nd derivatives
*******************************************/

function real fn_@(module_name);
input real t; 
input @filter_input_datatype si; 
input real xi0, xi1, yo0, yo1 @so_derivative @fn_input;
begin
  return @response_function;
end
endfunction

@(derivative_functions)

`protect
function real f2max_@(module_name);
input real t; 
input @filter_input_datatype si; 
input real xi0, xi1, yo0, yo1 @so_derivative @fn_input;
begin
  return @response_function_f2max;
end
endfunction

/*************************************
  Caluating Tintv
*************************************/

function real calculate_Tintv_@(module_name);
input real etol, t; 
input @filter_input_datatype si; 
input real xi0, xi1, yo0, yo1 @so_derivative @fn_input;
real abs_f2max;
begin
  abs_f2max = f2max_@(module_name)(t, si, xi0, xi1, yo0, yo1 @so_derivative @fn_input);
  return sqrt(8.0*etol/abs_f2max); 
end
endfunction
`endprotect

endmodule
