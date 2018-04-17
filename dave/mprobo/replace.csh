#!/bin/csh -f

set src = amschkconfig
set dst = environ
set tmpfile = tmp$$.csh
grep $src *py | awk 'BEGIN { FS = ":"} ; {print "sed -i s/'$src'/'$dst'/g " $1 }' > tmpfile
source tmpfile
rm tmpfile
