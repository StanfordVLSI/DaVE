// Regenerative latch

/******************* 
Note:
 1. Sampling aperture
  - This uses a simple aperture model from ADI's tutorial note. For given 'ta' (sampling aperture time), the effective sampled input is the one sampled with a delayed where the delay is ta/2.0. The inputs (inp, inn) may not be directly coupled to the outputs. If it is the case, there might be additional gain, which really sets the initial condition of the regenerative process. It means that the propagation phase described in the Abidi's paper is already taken into account.
  - The initial condition v0 for the regenerative process is then given by:
    v0 = gain*(pm.eval(inp,t0+ta/2.0)-pm.eval(inn,t0+ta/2.0)) where t0 is the rising(falling) edge of a sampling clock and ta is a sampling aperture time.

 2. Regeneration time calculation
  - The waveform of the differential outputs in the regenerative process is given by
    V(t) = v0*exp(t/tau) where tau is the regenerative time constant.
  - Assuming that vth is the logic threshold voltage of the quantization, the required time to resolve the outputs is given by
    td = tau*log(vth/abs(v0)).

 3. References
  - Sampling aperture: Aperture Time, Aperture Jitter, Aperture Delay Time— Removing the Confusion, ADI's MT-007 
  - Comparator: A. Abidi and H. Xu, Understanding the Regenerative Comparator Circuit, IEEE CICC 2014.

 4. Assumption
  - Reset phase is long enough not to cause any hysteresis issue.
*******************/ 

module $$(Module.name()) #(
  $$(Module.parameters())
) (
  $$(Module.pins())
);

timeunit 1fs;
timeprecision 1fs;

`protect
//pragma protect 
//pragma protect begin

`get_timeunit
PWLMethod pm=new;

$$Pin.print_map() $$# map between user pin names and generic ones

//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----

enum {RESET, SAMPLE, REGENERATION, DECISION} state;

wire i_clk;  // internal representation of a clock, clk
pwl supply; // effective supply voltage (vdd-vss)
real supply_r; // real var. of supply

$$# decalre real form of optional analog pins if exists
$$PWL.declare_real_optional_analog_pins()

event wakeup;
event init_wakeup; // wakeup for system's parameter initialization
real t0, tdiff;
real v0;
real dTr;
real v_icm_r;
pwl v_icm;

// declare model parameters
real tp; // $$Metric.description('tp')
real gain; // $$Metric.description('gain')
real tau; // $$Metric.description('tau')
real vth; // $$Metric.description('vth')

//----- FUNCTIONAL DESCRIPTION -----

initial state = RESET;
initial ->> init_wakeup;
assign i_clk = $$('clk' if Pin.constraint('clk', 'act_high') else '~clk');

//-- Compute input common-mode voltage
  pwl _v_icm[2]; real _k_v_icm[2];
  assign _v_icm = '{inp,inn};
  assign _k_v_icm = '{0.5, 0.5};
pwl_add #(.no_sig(2)) xicm (.in(_v_icm), .scale(_k_v_icm), .out(v_icm));

//-- System's parameter calculation

// handling supply
$$[if Pin.is_exist('vss')]
  pwl _vdd_vss[2]; real _k_vdd_vss[2];
  assign _vdd_vss = '{$$(Pin.name('vdd')),$$(Pin.name('vss'))};
  assign _k_vdd_vss = '{1.0, -1.0};
pwl_add #(.no_sig(2)) xsupply (.in(_vdd_vss), .scale(_k_vdd_vss), .out(supply));
$$[else]
assign supply = vdd;
$$[end if]


$$[if calibration_enabled()]

$$PWL.instantiate_pwl2real('supply')
$$PWL.instantiate_pwl2real_optional_analog_pins()

// calculating system's parameters
$${
## sensitivity list of the always blocks below
sensitivity = ['v_icm_r', 'supply_r', 'init_wakeup'] + PWL.list_real_optional_analog_pins() + Pin.list_optional_digital()

# model parameter mapping for back-annotation
model_param_map = { 'test1': {'tp':'tp', 'gain':'gain', 'tau':'tau', 'vth':'vth'} }
}$$

always @($$print_sensitivity_list(sensitivity)) begin
  t0 = `get_time;
$$annotate_modelparam(model_param_map)
end

$$[else]

initial begin
$${
for p in ['tp', 'gain', 'tau', 'vth']:
  pname = Param.prefix()+p
  if not Param.is_exist(pname):
    print put_warning_message("Paramter %s doesn't exist"%pname)
  else:
    print '  %s = %s;' %(p, pname)
}$$
end

$$[end if]

//-- Model behaviors

always @(negedge i_clk) begin // reset phase
  state = RESET;
  out = $$Pin.constraint('out', 'precharge');
  outb = $$Pin.constraint('outb', 'precharge');
end

always @(posedge i_clk) begin // sampling/propagation phases
  state = SAMPLE;
  ->> `delay(tp) wakeup;  
end

always @(wakeup) begin // regeneration or decision phase
  if (state==SAMPLE) begin  // regeneration
    state = REGENERATION;
    t0 = `get_time;
    v0 = gain*(pm.eval(inp,t0+tp/2.0)-pm.eval(inn,t0+tp/2.0)+v_os);
    dTr = max(TU,get_regeneration_delay(v0));
    ->> `delay(dTr) wakeup;
  end 
  else if (state==REGENERATION) begin // decision
    tdiff = `get_time - (t0+dTr);
    if (tdiff >= 0.0) begin 
      state = DECISION;
      out  <= (v0 >= 0)? 1'b1:1'b0;
      outb <= (v0 >= 0)? 1'b0:1'b1;
    end
    else
      ->> `delay(max(TU,-1.0*tdiff)) wakeup;
  end
end

// calculate delay to fire outputs in regeneration phase
function real get_regeneration_delay;
`input_real v0;
begin
  return tau*log(vth/abs(v0));
end
endfunction

//pragma protect end
`endprotect

endmodule
