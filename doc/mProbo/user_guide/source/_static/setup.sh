#!/bin/bash

# A sample setup file for DaVE in BASH
# Copyright (c) 2016 by Stanford University. All rights reserved.

export DAVE_INST_DIR="/cad/DaVE"
export DAVE_SAMPLES="${DAVE_INST_DIR}/samples"

export mLINGUA_DIR="${DAVE_INST_DIR}/mLingua"
export mLINGUA_DEMO_DIR="${mLINGUA_DIR}/examples"
export mLINGUA_SIMULATOR="vcs"
export mPROBO_DIR="${DAVE_INST_DIR}/mProbo"
export mPROBO_DEMO_DIR="${mPROBO_DIR}/examples"
export mGENERO_DIR="${DAVE_INST_DIR}/mGenero"
export mGENERO_DEMO_DIR="${mGENERO_DIR}/examples"

export PYTHONHOME="/cad/anaconda2/envs/dave"
if [ -z ${LD_LIBRARY_PATH} ]; then
  export LD_LIBRARY_PATH="${PYTHONHOME}/lib:${LD_LIBRARY_PATH}"
else
  export LD_LIBRARY_PATH="${PYTHONHOME}/lib"
fi

export PATH="${DAVE_INST_DIR}/bin:${PYTHONHOME}/bin:$PATH"

#########################################################################
# Loading simulator environments: modify these properly
# Development environment uses 
#   a. Cadence's INCISIVE to run Circuit/Verilog(-AMS) simulation
#   b. Synopsys' VCS to run Verilog simulation
#########################################################################
#module load incisive
#module load vcs
