*----------------------------------------------------------------------
* LAMBDA = 0.1 u, vdd=1.8 v
*----------------------------------------------------------------------
* Continous-time linear equalizer 
.SUBCKT ctle3 inp inn outp outn vdd vss $ctl<2> ctl<1> ctl<0>
I_1 vdd ibiasn DC 500u 
R_2 outp vdd 500 
R_1 outn vdd 500 
M_1 outn inp a vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_2 outp inn b vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_3 b ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_4 a ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_5 ibiasn ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
Xnmos_var v_fz b nmos_var M=2 lr='10u' wr='10u'
Xnmos_var_1 v_fz a nmos_var M=2 lr='10u' wr='10u'
R_3 a b 2k
vv_fz v_fz 0 dc 1.8

Cloadp outp vss 0.01p
Cloadn outn vss 0.01p
.ENDS	$ ctle3
