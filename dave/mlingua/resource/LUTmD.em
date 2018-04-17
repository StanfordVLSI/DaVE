/****************************************************************
 Module: @(module_name) 

 This is automatically generated multi-dimentional lookup table 
 model for choosing parameters of piecewise linear model
 depending on DC operating point

 Here are some assumptions:
  - All inputs are in PWL waveform format
  - All outputs are real (parameters to other block)

-----------------------------------------------------------------
 Copyright (c) 2014 by Byong Chan Lim. All rights reserved.

 The information and source code contained herein is the property
 of Byong Chan Lim, and may not be disclosed or reproduced
 in whole or in part without explicit written authorization from
 Byong Chan Lim.
-----------------------------------------------------------------
****************************************************************/

@# TODO: Indexing in SVerilog is computationally expensive, and I think there is a way to improve this.

@{
input_ports = x.keys()
output_ports = y.keys()
nDim = len(input_ports)
}@

module @(module_name) (
  input pwl @(', '.join(input_ports)),
  output real @(', '.join(output_ports))
);

// time scale can be changed as you want
timeunit 1fs;
timeprecision 1fs;


/////////////////////
// Look-up table info
/////////////////////
parameter integer nDim = @(nDim);
@[for p in input_ports]parameter integer x_@(p)_Size = @len(x[p]);
@[end for]
@[for p in input_ports]real lx_@(p)[x_@(p)_Size-1:0]; 
@[end for]
@{
xidx_str = ''
for p in input_ports:
  xidx_str += '[%s]' %('x_'+p+'_Size')

for p in output_ports:
  print 'real ly_%s%s;' %(p, xidx_str)
}@

/////////////////////
// Look-up table data
/////////////////////
initial begin

@{
for p in input_ports: 
  for i,d in enumerate(x[p]):
    print '%s[%d] = %f;' %('lx_'+p, i, d)

# Do this intelligently
rs = len(x[input_ports[0]])
cs = len(x[input_ports[1]])
for p in output_ports:
  for i in range(rs):
    for j in range(cs):
      print 'ly_%s[%d][%d] = %f;' %(p, i, j, y[p][i*cs+j])
}@

end


`protect
//////////////
// Process LUT
//////////////

`get_timeunit
PWLMethod pm=new;

reg event_in=1'b0;

pwl @(', '.join([p+'_prev' for p in input_ports]));
real @(', '.join([p+'0' for p in input_ports]));
integer @(', '.join(['index_'+p for p in input_ports]));

event wakeup;

time t_prev, dTm;
time dT=1;
real t;

real @(', '.join(['dt_'+p for p in input_ports]));

real dTr;

initial #1 ->> wakeup;

@{
evt_sense = ' or '.join(['`pwl_event('+p+')' for p in input_ports])
evt_df    = ' || '.join(['`pwl_check_diff(%s, %s_prev)' %(p, p) for p in input_ports])
evt_str   = ' '.join(['%s_prev = %s;' %(p, p) for p in input_ports])
evt_eval  = '\n    '.join(['%s0 = pm.eval(%s, t);' %(p, p) for p in input_ports])
evt_fidx  = '\n    '.join(['index_%s = find_index_%s_%s(%s0);' %(p, p, module_name, p) for p in input_ports])
idx_ref   = ''.join(['[index_%s]' %p for p in input_ports])
eval_out  = '\n    '.join(['%s = ly_%s%s;' %(p, p, idx_ref) for p in output_ports])
dt_cal    = '\n    '.join(['dt_%s = calculate_dt_%s_%s(index_%s, %s.b);' %(p, p, module_name, p, p) for p in input_ports])
def get_minstr(ports):
  if len(ports) == 1:
    return 'dt_'+ports[0]
  else:
    return 'min(dt_%s, %s)' %(ports[0], get_minstr(ports[1:]))

dt_min_str = 'dTr = ' + get_minstr(input_ports) + ';'
}@

always @@( @(evt_sense) or wakeup ) begin
  dTm = $realtime - t_prev;
  event_in = @evt_df;
  if (((dT==dTm)&&(dTm>=1)) || event_in) begin
    if (event_in) begin
      @evt_str
    end
    t = `get_time; // get current time

    // evaluate inputs at t
    @evt_eval         

    // find region
    @evt_fidx

    // retrieve outputs from LUT
    // I want this calculation simple, instead of doing multilinear interpolation
    @eval_out

    // calculate next event time interval (dt) for each input
    @dt_cal

    // select min(dt)
    @dt_min_str
    
    if (dTr < 1) begin
      dT = time'(dTr/TU);
      ->> #(dT) wakeup; // schedule an event after dT
      t_prev = $realtime;
    end
  end
end

// for given value, find the index of LUT (region)
@{
tpl='''
function integer find_index_{input}_{mname} (real value);
int idx[$];
begin
  if (value <= (lx_{input}[0])) return 0;
  if (value >= (lx_{input}[x_{input}_Size-1])) return x_{input}_Size-1;
  idx = lx_{input}.find_index with (item > value);
  return idx[0]-1;
end
endfunction
'''
for p in input_ports: 
  print tpl.format(input=p, mname=module_name)
}@

// calculate the next event where inflection of transfer curve 
// for given input (value, slope)
@{
tpl='''
function real calculate_dt_{input}_{mname}(integer index, real slope);
real sgn_sl;
real cur_val, nxt_val;
real dt;
begin
  sgn_sl = sgn(slope);
  cur_val = lx_{input}[index];
  nxt_val = cur_val;
  if ( (index == 0) && (sgn_sl<0) ) return 100;
  else if ( (index == (x_{input}_Size-1)) && (sgn_sl>0) ) return 100;
  else begin
    if (sgn_sl < 0) nxt_val = lx_{input}[index-1];
    else if (sgn_sl > 0) nxt_val = lx_{input}[index+1];
  end

  if (slope==0) return 100;
  else begin
    dt = (nxt_val-cur_val)/slope;
    if ((dt>=TU)) return dt;
    else return TU;
  end
end
endfunction
'''
for p in input_ports: 
  print tpl.format(input=p, mname=module_name)

}@

/***************************************************************
 Copyright (c) 2014 by Byong Chan Lim. All rights reserved.

 The information and source code contained herein is the property
 of Byong Chan Lim, and may not be disclosed or reproduced
 in whole or in part without explicit written authorization from
 Byong Chan Lim.
***************************************************************/

`endprotect

endmodule // end of "@module_name" module
