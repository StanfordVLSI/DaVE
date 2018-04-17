/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : mLingua_pwl.vh
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  Include header for PWL modeling.

* Note       :
  - To use resolution function of a pwl signal, define SV2012
    when running simulation. Note that this feature is enabled
    for recent version of SystemVerilog simulator 

* Revision   :
  - 7/26/2016: First release

****************************************************************/

/****************************************************
* Timeunit/precision of Verilog library modules
* Both timeunit and timeprecision will be the same
****************************************************/
`define DAVE_TIMEUNIT 1ps


/****************************************************
* PWL-related definition
****************************************************/

`ifndef AMS
  function real convert_realtime2real(realtime s);
  begin
    case(s)
      1fs   : return 1e-15;
      10fs  : return 1e-14;
      100fs : return 1e-13;
      1ps   : return 1e-12;
      10ps  : return 1e-11;
      100ps : return 1e-10;
      1ns   : return 1e-9;
      10ns  : return 1e-8;
      100ns : return 1e-7;
      1us   : return 1e-6;
      10us  : return 1e-5;
      100us : return 1e-4;
      1ms   : return 1e-3;
      10ms  : return 1e-2;
      100ms : return 1e-1;
      1s    : return 1.0;
    endcase
  end
  endfunction

  /////////////////////////////////
  //    pwl data structure
  /////////////////////////////////
  typedef struct {
    real a; // signal offset
    real b; // signal slope
    real t0;  // time offset
  } pwl;

  `ifdef SV2012
    ////////////////////////////////////////////////////////////
    // defining mpwl to handle multiple driver of pwl signals
    // Note:
    //  - Use `DAVE_TIMEUNIT as time unit and precision in a module
    //    where mpwl is defined
    ////////////////////////////////////////////////////////////
    // resolution function of "mpwl" nettype
    function automatic pwl res_mpwl (input pwl driver[]);
    real Isum_a=0;
    real Isum_b=0;
    real t;
    real TU=convert_realtime2real(`DAVE_TIMEUNIT);
    begin
      t = TU*$realtime; // current time
      foreach (driver[i]) begin // sum all the currents
        Isum_a += (driver[i].a + driver[i].b*(t-driver[i].t0)) ;
        Isum_b += driver[i].b ;
      end
      res_mpwl = '{Isum_a, Isum_b, t};
    end
    endfunction
  
    // nettype delcaration
    nettype pwl mpwl with res_mpwl;
  `endif


  ///////////////////////////////////
  // macro for real/pwl port
  ///////////////////////////////////
  `ifdef VCS
    `define input_pwl input pwl
    `define output_pwl output pwl
    `define input_real input real
    `define output_real output real
  `elsif NCVLOG
    `define input_pwl input var pwl
    `define output_pwl output var pwl
    `define input_real input var real
    `define output_real output var real
  `endif

  ///////////////////////////////////
  // constants for PWL value
  ///////////////////////////////////
  `define PWL1 '{1.0,0.0,0.0}
  `define PWL0 '{0.0,0.0,0.0}
  `define PWLZ '{0.0,0.0,-1.0} // Hi-Z

  //////////////////////////////////////////////////
  // collection of methods for processing PWL signal
  //////////////////////////////////////////////////
  class PWLMethod;
  
    // evaluate the current pwl value
    function real eval (pwl in, real t);
      return in.a + in.b*(t-in.t0);
    endfunction
  
    // write pwl struct
    function pwl write (real offset, real slope, real toffset);
    pwl out;
    begin
      out.a = offset; out.b = slope; out.t0 = toffset;
      return out;
    end
    endfunction
    
    // initialize pwl struct at t=0
    function pwl init (real __offset, real __slope);
      return write(__offset, __slope, 0.0);
    endfunction
    
    // update a pwl struct (slope only)
    function pwl update(pwl __signal, real __slope, real __toffset);
    real __offset;
    begin
      __offset = __signal.a + __signal.b*(__toffset-__signal.t0);
      return write(__offset, __slope, __toffset);
    end
    endfunction
  
    // project a pwl
    function pwl project(pwl __signal, real __toffset, real __newvalue, real __dT);
    real __offset, __slope;
    begin
      __offset = __signal.a + __signal.b*(__toffset-__signal.t0);
      __slope  = (__newvalue-__offset)/__dT;
      return write(__offset, __slope, __toffset);
    end
    endfunction
  
    // scale by a scalar
    function pwl scale(pwl __signal, real __scale, real __toffset);
      return write(__scale*__signal.a, __scale*__signal.b, __toffset);
    endfunction

    // add two pwl signals
    function pwl add(pwl sig1, pwl sig2, real scale1, real scale2, real tos);
      return write(scale1*eval(sig1,tos)+scale2*eval(sig2,tos), scale1*sig1.b+scale2*sig2.b, tos);
    endfunction

    // filtering event
    function pwl event_filter(pwl out_old, pwl out_new, real t, real etol);
    begin
      if (abs(eval(out_old, t)-out_new.a) > etol) return out_new;
      else return out_old;
    end
    endfunction
  
    // check if it is Hi-Z
    function is_hiz(pwl in);
    pwl hiz;
    begin
      hiz = `PWLZ;
      if ((in.a == hiz.a) && (in.b == hiz.b) && (in.t0 == hiz.t0)) return 1'b1;
      else return 1'b0;
    end
    endfunction

  endclass

  ////////////////////////
  // Real time calculation
  ////////////////////////

  `define get_timeunit real TU; initial $get_timeunit(TU);
  `define get_time  $realtime*TU
  `define delay(t) #((t)/TU)
  `define DT_MAX 1.0          // max value of allowed delta T [sec] for scheduling an event


  ////////////////////
  // PWL miscellaneous
  ////////////////////
  `define pwl_event(name) name.a or name.b  // expend pwl member variables for creating event sensitivity list in always @() statement
  `define pwl_check_diff(in, in_prev) in.a != in_prev.a || in.b != in_prev.b || in.t0 != in_prev.t0 // diff pwl member variables
  
`endif


/****************************************************
* Debugging & Assertions
****************************************************/

`ifndef AMS

  `define INFO(msg) $display("At t=%.3e [sec], [%m] ", $time*TU, msg) // display information

  // mutually exclusive
  `define ASSERT_MEX(sig1, sig2, msg) \
    always @(sig1 or sig2) begin \
      if ($time != 0) begin \
        $sformat(msg, "[%m] At t=%t [TU], %s and %s are mutually exclusive.", $time, `"sig1`", `"sig2`"); \
        assert (sig1 ^ sig2) else $warning(msg); \
      end \
    end // assert if sig1 & sig2 are mutually exclusive

  // never both be high
  `define ASSERT_NAND(sig1, sig2, msg) \
    always @(sig1, sig2) begin \
      if ($time != 0) begin \
        $sformat(msg, "[%m] At t=%t [TU], %s and %s can't be both high.", $time, `"sig1`", `"sig2`"); \
        assert (~(sig1 & sig2)) else $warning(msg); \
      end \
    end // assert if sig1 & sig2 are mutually exclusive

`endif

/****************************************************
* Math
****************************************************/
`ifndef AMS

  import "DPI-C" pure function real exp(input real x);
  import "DPI-C" pure function real log(input real x);
  import "DPI-C" pure function real log10(input real x);
  import "DPI-C" pure function real sqrt(input real x);
  import "DPI-C" pure function real sin(input real x);
  import "DPI-C" pure function real cos(input real x);
  import "DPI-C" pure function real floor(input real x);
  
  `define M_PI 3.14159265358979323846   // pi in radian
  `define M_TWO_PI (2.0*`M_PI) // two-pi in radian
  `define rdist_normal(s,n) $dist_normal(s, 0, n)/(1.0*n)   // generate normal dist.
  `define rdist_uniform(s,n) $dist_uniform(s, 0, n)/(1.0*n)   // generate uniform dist.

  function real min(real a0, real a1);  // min of two numbers
    if (a0 >= a1) return a1;
    else return a0;
  endfunction

  function real max(real a0, real a1);  // max of two numbers
    if (a0 >= a1) return a0;
    else return a1;
  endfunction

  function integer is_pinf(real x); // check if +inf
    if (x == 1.0/0.0) return 1;
    else return 0;
  endfunction

  function integer sgn(real x); // return sign of a number
  begin
    if (x > 0.0) return 1;
    else if(x < 0.0) return -1;
    else return 0;
  end
  endfunction
  
  function real abs(real x);  // return absolute value
  begin
    if (x == -0) return 0;
    if (sgn(x) == -1) return x*-1.0;
    else return x;
  end
  endfunction

  function bit isnan (real x);  // check if it is Not-a-Number
  reg [63:0] r2b;
  begin
    r2b = x;
    if (r2b == 0) return 1'b1;
    else return 1'b0;
  end
  endfunction

`endif

/****************************************************
* Random seed generation
****************************************************/
`ifndef AMS

  `define generate_random_seed(m_seed, offset) \
    int seed; \
    //`ifdef VCS \
      initial begin \
        if ($test$plusargs("seed")) $value$plusargs("seed=%d",seed); else seed = m_seed; \
        seed = seed + offset; \
      end \
    //`endif

`endif

/****************************************************
* Miscellaneous
****************************************************/

`ifndef AMS

  /////////////////////////////////////////////////
  // run_wave macro for dumping waveforms to a file
  /////////////////////////////////////////////////
  `ifdef VCS
    `define run_wave  \
      initial begin \
        if ( $test$plusargs("wave") ) begin \
          $vcdpluson(0, test); \
          $vcdplusmemon(0, test); \
        end \
      end
  `elsif NCVLOG // use tcl script instead
    `define run_wave  \
      initial begin \
        //$shm_open("waves.shm"); \
        //$shm_probe(); \
      end
  `endif

  ///////////////////////////////////////////////////////
  // log2(val) to calculate # of bits to represents "val"
  ///////////////////////////////////////////////////////
  function integer log2;
  input integer val;
  begin
   log2 = 0;
   while (val > 0) begin
      val = val >> 1;
    log2 = log2 + 1;
   end
  end
  endfunction

`endif

`include "mLingua_util.vh"
