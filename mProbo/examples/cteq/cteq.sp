*----------------------------------------------------------------------
* LAMBDA = 0.1 u, vdd=1.8 v
*----------------------------------------------------------------------
* Continous-time linear equalizer 
* The generation resistor is controlled by v_fz input
.SUBCKT cteq vinp vinn voutp voutn v_fz vdd vss $ctl<2> ctl<1> ctl<0>
I_1 vdd ibiasn DC 500u 
R_2 voutp vdd 1k 
R_1 voutn vdd 1k 
M_1 voutn vinp a vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_2 voutp vinn b vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_3 b ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_4 a ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_5 ibiasn ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
Xnmos_var vdd b nmos_var M=8 lr='10u' wr='10u'
Xnmos_var_1 vdd a nmos_var M=8 lr='10u' wr='10u'
gvcr a b vcr pwl(1) v_fz vss 0v,1k 1.8v,3k  $ VCR

Cloadp voutp vss 0.01p
Cloadn voutn vss 0.01p
.ENDS	$ cteq

.subckt sw g d s
g d s pwl(1) g 0  0,10meg  1.8,1m  level=1
.ends
