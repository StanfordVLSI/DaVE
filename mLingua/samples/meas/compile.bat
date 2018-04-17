set vlogcmd = 'ncvlog -cdslib /home/bclim/cktbook/opusdb/cds.lib -ams -use5x -work dave_prim -view verilogams'

find . -maxdepth 1 -name "*.va" -exec $vlogcmd {} \;
