#!/bin/csh -f

find . -name "*.txt" -exec rm {} \;
find . -name "*.eps" -exec rm {} \;
find . -name "*.tr0" -exec rm {} \;
find . -name "*.st0" -exec rm {} \;
find . -name "*.lis" -exec rm {} \;

