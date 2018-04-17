$
.subckt pre_amp2 avdd clk ibn inn inp outn outp pdn
m0 net015 net16 0 0 nmos L=500e-9 W=1e-6 M=1
mnm96 ibn pdn net16 0 nmos L=180e-9 W=2e-6
rdummy ibn 0 1meg
mnm63 net20 net16 0 0 nmos L=500e-9 W=1e-6 M=6
mnm1 outp inn net20 0 nmos L=180e-9 W=2.4e-6 M=1
mnm0 outn inp net20 0 nmos L=180e-9 W=2.4e-6 M=1
mnm62 net16 net16 0 0 nmos L=500e-9 W=1e-6
mpm1 outp clk outn avdd pmos L=180e-9 W=720e-9
mpm7 outp net015 avdd avdd pmos L=300e-9 W=380e-9 M=2
mpm11 outp outp avdd avdd pmos L=300e-9 W=300e-9 M=1
mpm10 outn outn avdd avdd pmos L=300e-9 W=300e-9 M=1
mpm6 outn net015 avdd avdd pmos L=300e-9 W=380e-9 M=2
mpm35 net015 net015 avdd avdd pmos L=300e-9 W=380e-9 M=1
cloadp outp 0 4f
cloadn outn 0 4f
.ends pre_amp2

