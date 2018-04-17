#!/bin/sh

rm -rf connectLib
mkdir connectLib

# compiling the connect module and the connect rules
ncvlog -ams -work connectLib *.vams -64BIT 

rm *.log
