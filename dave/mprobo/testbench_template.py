__doc__ = '''
empy template for a testbench
'''

from StringIO import StringIO


tb_template = StringIO("""
@# Template for test bench
@{
from dave.mprobo.environ import EnvTestcfgTestbench, EnvTestcfgSection, EnvTestcfgSimTime, EnvSimcfg
}@
@{_tenvtb = EnvTestcfgTestbench()}
@{_tenvs  = EnvTestcfgSection()}
@{_tenvts = EnvTestcfgSimTime()}
@{_tenvsc = EnvSimcfg()}
@[if model == _tenvtb.model_ams]
`include "disciplines.vams"
`include "constants.vams"
@[end if]

@[if hdl_include_files != ['']]
@[for i in hdl_include_files]
`include "@i"
@[end for]
@[end if]

@testbench[_tenvs.pre_module_declaration]

`timescale @simulation[_tenvts.sim_timeunit]/@simulation[_tenvts.sim_timeunit]
///////////////////////////////////////////////////////////////////////////
// @test_name testbench 
///////////////////////////////////////////////////////////////////////////
//module @test_name;
module test;

///////////////////////////////////////////////////////////////////////////
// declaration of wire, real(or electrical) signals for internal connection
///////////////////////////////////////////////////////////////////////////
@[for p,v in testbench[_tenvs.wire][model].items()] @[for x in v] 
@p @x; 
@[end for] @[end for]

///////////////////////////////////////////////////////////////////////////
// initial condition if Verilog
///////////////////////////////////////////////////////////////////////////
@[if model == _tenvtb.model_verilog]
initial begin
@[for p,v in initial_condition.items()]
force test.@p = @v ;
@[end for]
#1;
@[for p,v in initial_condition.items()]
release test.@p ;
@[end for]
end
@[end if]

///////////////////////////////////////////////////////////////////////////
// Custom code here
///////////////////////////////////////////////////////////////////////////
@testbench[_tenvs.tb_code] 

///////////////////////////////////////////////////////////////////////////
// instantiation of modules
///////////////////////////////////////////////////////////////////////////
@[for p in testbench[_tenvs.instance]]
@p @[end for]

///////////////////////////////////////////////////////////////////////////
// instantiation of file dump statement
///////////////////////////////////////////////////////////////////////////
@[for p,v in testbench[_tenvs.response].items()]
@[if p != _tenvtb.meas_filename]
@v[_tenvtb.meas_blk]
@[end if]
@[end for]

@[if simulator == _tenvsc.vcs]
initial begin
  $vcdpluson(0,test);
  $vcdplusmemon(0,test);
end
@[end if]

///////////////////////////////////////////////////////////////////////////
// simulation time control
///////////////////////////////////////////////////////////////////////////
@{
from dave.common.misc import from_engr
}@
initial #(@(int(round(from_engr(simulation[_tenvts.sim_time].rstrip('s'))/from_engr(simulation[_tenvts.sim_timeunit].rstrip('s')))))) $finish;

endmodule
""")
