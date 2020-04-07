/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : meas_clock.v
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: It measures properties of a clock signal such as
  frequency, duty-cycle, etc.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

// include files as necessary
`ifdef AMS
    `include "disciplines.vams"
`else
    `include "mLingua_pwl.vh"
`endif

module meas_clock #(
    parameter dir = 1'b1,          // invert clk if dir = 1'b0
    parameter real vlth = 0.5,     // logic threshold in proportion to vdd,
                                   // valid only for Verilog-AMS
    parameter real tstart = 0.0    // measurement starts after time "tstart"
) (
    `ifdef AMS
        input clk,
        input vdd,
        output frequency,
        output period,
        output dutycycle
    `else
        input clk,
        `input_pwl vdd,
        `output_pwl frequency,
        `output_pwl period,
        `output_pwl dutycycle
    `endif
);
    `ifdef AMS
        // declare the signal type for I/O
        electrical clk;
        electrical vdd;
        electrical frequency;
        electrical period
        electrical dutycycle;
    `else
        // declare timestep
        timeunit `DAVE_TIMEUNIT ;
        timeprecision `DAVE_TIMEUNIT ;
        // set up PWL
        `get_timeunit
        PWLMethod pm=new;
    `endif

    // internal variables
    real t_pos0, t_pos, t_neg, rfreq, rperiod, rdutycycle;

    // assign to clk_int
    `ifdef AMS
        reg clk_int;
        always @(cross(V(clk)-V(vdd)*vlth,+1)) begin
            clk_int = dir ? 1'b1: 1'b0;
        end
        always @(cross(V(clk)-V(vdd)*vlth,-1)) begin
            clk_int = dir ? 1'b0 : 1'b1;
        end
    `else
        wire clk_int;
        assign clk_int = dir ? clk : ~clk;
    `endif

    // for AMS models: drive output signals
    `ifdef AMS
        initial begin
            rfreq = 1;
        end
        analog begin
            V(frequency) <+ rfreq;
            V(period) <+ rperiod;
            V(dutycycle) <+ rdutycycle;
        end
    `endif

    // main logic to compute the period
    always @(posedge clk_int) begin
        // get the current time in seconds
        `ifdef AMS
            t_pos = $abstime;
        `else
            t_pos = `get_time;
        `endif

        // compute the frequency
        if ((t_pos0 > 0.0) && (t_pos >= tstart) && (t_pos != t_pos0)) begin
            rfreq = 1.0/(t_pos-t_pos0);
        end

        // compute the period
        rperiod = 1.0/rfreq;

        // compute the duty cycle
        rdutycycle = (t_neg-t_pos0)/rperiod;

        // save the time of this positive edge
        t_pos0 = t_pos;

        // for non-AMS models, write to output signals
        `ifndef AMS
            frequency = pm.write(rfreq, 0.0, 0.0);
            period = pm.write(rperiod, 0.0, 0.0);
            dutycycle = pm.write(rdutycycle, 0.0, 0.0);
        `endif
    end

    // record the time of the negative edge
    always @(negedge clk_int) begin
        `ifdef AMS
            t_neg = $abstime;
        `else
            t_neg = `get_time;
        `endif
    end
endmodule