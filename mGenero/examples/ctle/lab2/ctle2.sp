*----------------------------------------------------------------------
* LAMBDA = 0.1 u, vdd=1.8 v
*----------------------------------------------------------------------
* Continous-time linear equalizer 
* The generation resistor is controlled by v_fz input
.SUBCKT ctle2 inp inn outp outn vdd vss drctl<1> drctl<0>
I_1 vdd ibiasn DC 500u 
R_2 outp vdd 1k 
R_1 outn vdd 1k 
M_1 outn inp a vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_2 outp inn b vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=5
M_3 b ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_4 a ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
M_5 ibiasn ibiasn vss vss nmos W='250*0.1u' L='4*0.1u' GEO=1 M=4
Xnmos_var vdd b nmos_var M=8 lr='10u' wr='10u'
Xnmos_var_1 vdd a nmos_var M=8 lr='10u' wr='10u'

R_6 a a2 8k
R_7 b2 b 8k
x2 drctl<1> a2 b2 sw
R_8 a a3 8k
R_9 b3 b 8k
x3 drctl<0> a3 b3 sw
R_10 a a4 2k
R_11 b4 b 2k
x4 vdd a4 b4 sw

Cloadp outp vss 0.01p
Cloadn outn vss 0.01p
.ENDS	$ ctle2

.subckt sw g d s
g d s pwl(1) g 0  0,10meg  1.8,1m  level=1
.ends
