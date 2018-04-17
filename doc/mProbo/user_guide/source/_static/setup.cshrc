#!/bin/csh -f

# A sample setup file for DaVE in C-SHELL
# Copyright (c) 2016 by Stanford University. All rights reserved.

setenv DAVE_INST_DIR /cad/DaVE
setenv DAVE_SAMPLES ${DAVE_INST_DIR}/samples

setenv mLINGUA_DIR ${DAVE_INST_DIR}/mLingua
setenv mLINGUA_DEMO_DIR ${mLINGUA_DIR}/examples
setenv mLINGUA_SIMULATOR vcs
setenv mPROBO_DIR ${DAVE_INST_DIR}/mProbo
setenv mPROBO_DEMO_DIR ${mPROBO_DIR}/examples
setenv mGENERO_DIR ${DAVE_INST_DIR}/mGenero
setenv mGENERO_DEMO_DIR ${mGENERO_DIR}/examples

setenv PYTHONHOME /cad/anaconda2/envs/dave
if ( $?LD_LIBRARY_PATH ) then
  setenv LD_LIBRARY_PATH ${PYTHONHOME}/lib:${LD_LIBRARY_PATH}
else
  setenv LD_LIBRARY_PATH ${PYTHONHOME}/lib
endif

set path = ( ${DAVE_INST_DIR}/bin ${PYTHONHOME}/bin $path )

#########################################################################
# Loading simulator environments: modify these properly
# Development environment uses 
#   a. Cadence's INCISIVE to run Circuit/Verilog(-AMS) simulation
#   b. Synopsys' VCS to run Verilog simulation
#########################################################################
#module load base
#module load incisive
#module load vcs
