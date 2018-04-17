
** Library name: pll_zero_phos_ptm065
** Cell name: vco_lvsft
** View name: schematic
.subckt vco_lvsft in inb out outb vdd_in
m1 out inb 0 0 nmos L=0.08u W=1.8u
m0 outb in 0 0 nmos L=0.08u W=1.8u
m5 outb outb vdd_in vdd_in pmos L=0.08u W=0.3u
m4 out out vdd_in vdd_in pmos L=0.08u W=0.3u
m3 outb out vdd_in vdd_in pmos L=0.08u W=0.3u
m2 out outb vdd_in vdd_in pmos L=0.08u W=0.3u
.ends vco_lvsft
** End of subcircuit definition.

** Library name: schema
** Cell name: inv
** View name: schematic
.subckt inv_pcell_0 a y localpwr
m1 y a localpwr localpwr pmos L=0.08u W=0.8u M=2
m2 y a 0 0 nmos L=0.08u W=1.6u M=2
.ends inv_pcell_0
** End of subcircuit definition.

** Library name: schema
** Cell name: inv
** View name: schematic
.subckt inv_pcell_1 a y localpwr
m1 y a localpwr localpwr pmos L=0.08u W=0.8u
m2 y a 0 0 nmos L=0.08u W=1.6u
.ends inv_pcell_1
** End of subcircuit definition.

** Library name: pll_zero_phos_ptm065
** Cell name: ringosc
** View name: schematic
.subckt ringosc_sub ck ckb vreg
xu9 p4 p0 vreg inv_pcell_0
xu4 m4 m0 vreg inv_pcell_0
xu13 m0 ckb vreg inv_pcell_1
xu12 p0 m0 vreg inv_pcell_1
xu11 m0 p0 vreg inv_pcell_1
xu10 p3 p4 vreg inv_pcell_1
xu8 p0 p1 vreg inv_pcell_1
xu7 p1 p2 vreg inv_pcell_1
xu6 p2 p3 vreg inv_pcell_1
xu5 p0 ck vreg inv_pcell_1
xu3 m3 m4 vreg inv_pcell_1
xu2 m2 m3 vreg inv_pcell_1
xu1 m1 m2 vreg inv_pcell_1
xu0 m0 m1 vreg inv_pcell_1
.ends ringosc_sub
** End of subcircuit definition.

** Library name: schema
** Cell name: inv
** View name: schematic
.subckt inv_pcell_2 a y localpwr
m1 y a localpwr localpwr pmos L=0.08u W=0.3u
m2 y a 0 0 nmos L=0.08u W=0.3u
.ends inv_pcell_2
** End of subcircuit definition.

** Library name: pll_zero_phos_ptm065
** Cell name: vco_dtos
** View name: schematic
.subckt vco_dtos in inb out vdd_in
m1 net16 inb vdd_in vdd_in pmos L=0.08u W=0.3u
m0 net13 in vdd_in vdd_in pmos L=0.08u W=0.3u
m3 net13 net13 0 0 nmos L=0.08u W=0.3u
m2 net16 net13 0 0 nmos L=0.08u W=0.3u
xu1 net21 out vdd_in inv_pcell_2
xu0 net16 net21 vdd_in inv_pcell_2
.ends vco_dtos
** End of subcircuit definition.

** Library name: schema
** Cell name: inv
** View name: schematic
.subckt inv_pcell_3 a y localpwr
m1 y a localpwr localpwr pmos L=0.08u W=0.48u
m2 y a 0 0 nmos L=0.08u W=0.24u
.ends inv_pcell_3
** End of subcircuit definition.

** Library name: pll_zero_phos_ptm065
** Cell name: vco
** View name: schematic

.subckt ringosc vdd vreg cko ckob
xi0 vcock vcockb lck lckb vdd vco_lvsft
xvco vcock vcockb vreg ringosc_sub
xi3 lckb lck net013 vdd vco_dtos
xi2 lck lckb net9 vdd vco_dtos
xu1 net013 cko vdd inv_pcell_3
xu0 net9 ckob vdd inv_pcell_3
.ends
