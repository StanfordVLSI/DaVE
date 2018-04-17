#!/bin/csh -f

set src = tb_code
set dst = tb_code
set tmpfile = tmp$$.csh
grep -R $src * | awk 'BEGIN { FS = ":"} ; {print "sed -i s/'$src'/'$dst'/g " $1 }' > tmpfile
#source tmpfile
#rm tmpfile
