
** Library name: tcbn65gplus
** Cell name: CKND2D0
** View name: schematic
.subckt CKND2D0 a1 a2 vdd vss zn
m0 zn a1 net1 vss nmos l=60e-9 w=195e-9 m=1 
m1 net1 a2 vss vss nmos l=60e-9 w=195e-9 m=1 
m2 zn a2 vdd vdd pmos l=60e-9 w=195e-9 m=1 
m3 zn a1 vdd vdd pmos l=60e-9 w=195e-9 m=1 
.ends CKND2D0
** End of subcircuit definition.

** Library name: mProbo_example
** Cell name: CKND2D1_sym
** View name: schematic
.subckt CKND2D1_sym a1 a2 vdd vss zn
xi1 a1 a2 vdd vss zn CKND2D0
xi2 a2 a1 vdd vss zn CKND2D0
.ends CKND2D1_sym
** End of subcircuit definition.

** Library name: tcbn65gplus
** Cell name: CKND2
** View name: schematic
.subckt CKND2 i vdd vss zn
m_u1_0 zn i vdd vdd pmos l=60e-9 w=520e-9 m=1 
m_u1_1 zn i vdd vdd pmos l=60e-9 w=520e-9 m=1 
m_u2_1 zn i vss vss nmos l=60e-9 w=310e-9 m=1 
m_u2_0 zn i vss vss nmos l=60e-9 w=310e-9 m=1 
.ends CKND2
** End of subcircuit definition.

** Library name: mProbo_example
** Cell name: pll_pfdhalf
** View name: schematic
.subckt pll_pfdhalf vdd vss in rst up
m5 net5 u vss vss nmos l=60e-9 w=310e-9 m=2 
m1 net026 in net5 vss nmos l=60e-9 w=310e-9 m=2 
m0 u rst vss vss nmos l=60e-9 w=150e-9 m=1 
m4 net026 u vdd vdd pmos l=60e-9 w=520e-9 m=1 
m3 net28 rst vdd vdd pmos l=60e-9 w=520e-9 m=1 
m2 u in net28 vdd pmos l=60e-9 w=520e-9 m=1 
xi0 net026 vdd vss up CKND2
.ic v(up)=0 v(dn)=0
.ends pll_pfdhalf
** End of subcircuit definition.

** Library name: tcbn65gplus
** Cell name: CKND2D1
** View name: schematic
.subckt CKND2D1 a1 a2 vdd vss zn
m0 zn a1 net1 vss nmos l=60e-9 w=390e-9 m=1 
m1 net1 a2 vss vss nmos l=60e-9 w=390e-9 m=1 
m2 zn a1 vdd vdd pmos l=60e-9 w=390e-9 m=1 
m3 zn a2 vdd vdd pmos l=60e-9 w=390e-9 m=1 
.ends CKND2D1
** End of subcircuit definition.

** Library name: mProbo_example
** Cell name: pfd
** View name: schematic
.subckt pfd2 vdd refclk fbclk up down 
xi5 up down vdd 0 net29 CKND2D1_sym
xi4 vdd 0 fbclk rst down pll_pfdhalf
xi0 vdd 0 refclk rst up pll_pfdhalf
xi3 net29 rstb vdd 0 rst CKND2D1
xi1 0 vdd 0 rstb CKND2
.ends pfd2
