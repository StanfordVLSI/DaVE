$$$

*** sim parameters 
.param ps = 1.8
+ vc = 1.6
+ swing = 0.2

*** balun for single-diff conversion
$.subckt balun   vdm     vcm     vp      vm
$e1      vp      vcm     transformer     vdm     0    1
$e2      vcm     vm      transformer     vdm     0    1
$.ends balun

*** LIB
.lib "/home/bclim/proj/DaVEnv/mProbo/examples/spice_lib/ptm180/models.lib" tt 

.include '../ctle.sp'

*** DUT
xbalun vdm vcm inp inn balun
xctle inp inn outp outn v_fz vdd vss ctle

*** testbench
vcm vcm 0 dc vc
vdm vdm 0 dc 0 ac 1
vdd vdd vss dc ps
vss vss gnd dc 0
v_fz v_fz vss dc 0

*** analysis
$.dc vcm 0 'ps+1.0' 0.01 $ DC to get vic_max, itotal
$.dc vdm '-2*swing' '2*swing' 0.001 $ DC to get  vout_min
.ac dec 100 1meg 20g sweep v_fz 0 ps 0.1 $ AC to get zero, two poles, gain

.options post accurate=1 post_version=9605
$.probe dc gmo(xctle.minp_r) gmo(xctle.minn_r)
$.probe dc i(xctle.mct1)
.probe ac v(outp,outn)
.end
