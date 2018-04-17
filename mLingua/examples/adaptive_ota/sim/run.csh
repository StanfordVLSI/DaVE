#!/bin/csh -f

echo "\n======================================================"
echo "Running under `pwd`"
make >& /dev/null
make clean >& /dev/null
