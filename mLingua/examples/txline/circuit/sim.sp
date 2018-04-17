* Stripline circuit
.param Z0 = 50.0
+ TD = 0.55e-9
+ RT = 35
+ RR = 1k
+ IOUT = 10e-3

.OPTION Post method=gear
$vIN s 0 PWL 0 0v 250ps 0v 350ps 0.01
$Rts s s1 50
$Tin s1 0 d 0 ZO=50 TD=0.17ns
iIN 0 s pulse (0 IOUT 10e-9 10p 10p '0.5e-9-10p' 2)
Rtterm s 0 RT
Rrterm d 0 RR
Tin s 0 d 0 ZO=Z0 TD=TD

.tran 5p 200n

.end

