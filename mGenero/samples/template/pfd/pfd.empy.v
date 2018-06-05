/*******************************************
* Phase frequency detector
*******************************************/

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

`get_timeunit // get timeunit using a PLI and assign it to TU
PWLMethod pm=new; // A class of methods for evaluating PWL waveform

$$Pin.print_map()

//----- BODY STARTS HERE -----

//----- SIGNAL DECLARATION -----
reg up=1'b0;
reg dn=1'b0;

reg i_ckref, i_ckfb; 
wire rst;
real t0;
event init_wakeup; // wakeup for system's parameter initialization



pwl supply; // effective supply voltage (vdd-vss)
real supply_r; // real var. of supply

$$# decalre real form of optional analog pins if exists
$$PWL.declare_real_optional_analog_pins()

// declare model parameters
real tpd; // $$Metric.description('tpd')
real tos; // $$Metric.description('tos')
real rstpw; // $Mmetric.description('rstpw')

//----- FUNCTIONAL DESCRIPTION -----

initial ->> init_wakeup;

$$# handling external reset
$${
if Pin.is_exist('reset'):
  ext_reset_expr = '~' if not Pin.constraint('reset', 'act_high') else '' + Pin.name('reset') + ' |'
else:
  ext_reset_expr = ''
}$$

assign rst = $$(ext_reset_expr) (up & dn); // reset pfd

// initialization if reset doesn't exists
$$[if not Pin.is_exist('reset')]
initial begin
  force rst=1'b1;
  #1 release rst;
end
$$[end if]

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

$$PWL.instantiate_pwl2real('supply')
$$PWL.instantiate_pwl2real_optional_analog_pins()

// calculating system's parameters
$${
## sensitivity list of the always blocks below
sensitivity = ['supply_r', 'init_wakeup'] + PWL.list_real_optional_analog_pins() + Pin.list_optional_digital()
sensitivity = ['reset'] + sensitivity if Pin.is_exist('reset') else sensitivity

# model parameter mapping for back-annotation
model_param_map = { 'test2': {} }
if Metric.is_exist('tpd'): model_param_map['test2'].update({'tpd':'tpd'})
if Metric.is_exist('tos'): model_param_map['test2'].update({'tos':'tos'})
if Metric.is_exist('rstpw'): model_param_map['test2'].update({'rstpw':'rstpw'})
}$$

always @($$print_sensitivity_list(sensitivity)) begin
  t0 = `get_time;
$$[if not Metric.is_exist('tpd')]  tpd = 0.0;$$[end if]
$$[if not Metric.is_exist('tos')]  tos = 0.0;$$[end if]
$$[if not Metric.is_exist('rstpw')]  rstpw = 0.0;$$[end if]

$$annotate_modelparam(model_param_map)
end

//-- Model behaviors

$$# handling clock edges
// delay inputs for propagation delay property
always @(ckref) 
  i_ckref = `delay(tpd) $$[if not Pin.constraint('ckref','pos_edge')]~$$[end if]$$(Pin.name('ckref'));

always @(ckfb) begin
  i_ckfb = `delay(tpd+tos) $$[if not Pin.constraint('ckfb','pos_edge')]~$$[end if]$$(Pin.name('ckfb'));
end

// PFD operation
always @(posedge i_ckref or posedge rst) begin
  if (rst) `delay(rstpw) up <= 0;
  else up <= 1'b1;
end

always @(posedge i_ckfb or posedge rst) begin
  if (rst) `delay(rstpw) dn <= 0;
  else dn <= 1'b1;
end

//pragma protect end
`endprotect

endmodule
