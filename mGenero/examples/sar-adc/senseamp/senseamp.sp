** Cell name: senseamp
** View name: schematic
.subckt senseamp avdd clk_latch outn outp vin vip
mpm11 xnn clk_latch avdd avdd pmos L=180e-9 W=300e-9
mpm10 outn clk_latch avdd avdd pmos L=180e-9 W=300e-9
mpm2 outn outp avdd avdd pmos L=180e-9 W=900e-9
mpm1 outp outn avdd avdd pmos L=180e-9 W=900e-9
mpm8 outp clk_latch avdd avdd pmos L=180e-9 W=300e-9
mpm9 xnp clk_latch avdd avdd pmos L=180e-9 W=300e-9
mnm11 xnn vip s 0 nmos L=180e-9 W=2e-6
mnm1 outn outp xnn 0 nmos L=180e-9 W=500e-9
mnm9 s clk_latch 0 0 nmos L=180e-9 W=2e-6 M=2
mnm0 outp outn xnp 0 nmos L=180e-9 W=500e-9
mnm10 xnp vin s 0 nmos L=180e-9 W=2e-6
.ends senseamp
** End of subcircuit definition.
