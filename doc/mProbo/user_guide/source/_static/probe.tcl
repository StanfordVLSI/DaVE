# probe.tcl for ncsimulator
database -open test.shm -into test.shm -default
probe -creat -shm -all -depth all
run
exit
