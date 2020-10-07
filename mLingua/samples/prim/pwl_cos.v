/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : pwl_cos.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  - This outputs a cosine waveform in pwl.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

`include "mLingua_pwl.vh"

module pwl_cos #(
    parameter real etol=0.0001,    // error tolerance of PWL approximation
    parameter real freq=100e6,     // frequency
    parameter real amp=0.01,       // amplitude
    parameter real offset=0.01,    // DC offset
    parameter real ph=0.0          // initial phase in degrees
) (
    `output_pwl out                // cosine output in pwl
);
    // set timing options
    timeunit `DAVE_TIMEUNIT;
    timeprecision `DAVE_TIMEUNIT;

    // instantiate object for PWL updates
    PWLMethod pm=new;

    // wires
    event  wakeup;    // event signal
    real phase;
    real dPhase;
    real t_cur;        // current time
    real out_cur;      // current output signal value
    real out_nxt;      // out at (t_cur+dT) for pwl output data
    real dT;           // time interval of PWL waveform
    real out_slope;    // out slope

    // you may need some additional wire definitions here
    initial begin
      phase = ph/180*(`M_PI);
      dPhase = 0.0;
      ->> wakeup;
    end

    always @(wakeup) begin
        // get current time
        t_cur = ($realtime/1s);

        // update phase, wrapping as necessary
        // TODO: should modular arithmetic be used here instead?
        // The potential issue is that the phase update is greater
        // than 2*pi.  That shouldn't normally happen but is possible
        // in some corner cases.
        phase = phase + dPhase;
        if (phase >= 2*(`M_PI)) begin
            phase = phase - (2*(`M_PI));
        end

        // calculate current output
        out_cur = fn_pwl_cos(phase);

        // calculate next wakeup time
        dT = calculate_Tintv_pwl_cos(etol, phase);

        // calculate phase at next wakeup time
        dPhase = (2*(`M_PI))*freq*dT;

        // calculate value at next wakeup time
        out_nxt = fn_pwl_cos(phase+dPhase);

        // calculate slope between current value and next wakeup time
        out_slope = (out_nxt-out_cur)/dT;

        // write current output value and calculated slope to the output
        out = pm.write(out_cur, out_slope, t_cur);

        // trigger wakeup at some time in the future
        ->> #(dT*1s) wakeup;
    end

    // Value of the cosine function

    function real fn_pwl_cos(input real phase);
        return offset + amp*cos(phase);
    endfunction

    // Maximum second derivative of the cosine

    function real f2max_pwl_cos(input real phase);
        return abs(amp*(2*(`M_PI)*freq)**2);
    endfunction

    // Caluating Tintv

    function real calculate_Tintv_pwl_cos(input real etol, input real phase);
        // internal variables
        real abs_f2max;
        real calcT;

        // calculate maximum second derivative of the cosine
        abs_f2max = f2max_pwl_cos(phase);

        // convert this second derivative to a time based
        // on the allowed error tolerance
        calcT = sqrt(8.0*etol/abs_f2max);

        // return timestep, clamped between the min/max limits
        return min(`DT_MAX, max((`DAVE_TIMEUNIT)/1s, calcT));
    endfunction

endmodule
