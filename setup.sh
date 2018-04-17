#!/bin/bash

# A sample setup file for DaVE
# Copyright (c) 2014-2016 by Byong Chan Lim. All rights reserved.

export DAVE_INST_DIR="/home/bclim/proj/StanfordVLSI/DaVE"
export DAVE_SAMPLES="${DAVE_INST_DIR}/samples"

export mLINGUA_DIR="${DAVE_INST_DIR}/mLingua"
export mLINGUA_DEMO_DIR="${mLINGUA_DIR}/examples"
export mLINGUA_SIMULATOR="ncsim"  # vcs or ncsim
export mPROBO_DIR="${DAVE_INST_DIR}/mProbo"
export mPROBO_DEMO_DIR="${mPROBO_DIR}/examples"
export mGENERO_DIR="${DAVE_INST_DIR}/mGenero"
export mGENERO_DEMO_DIR="${mGENERO_DIR}/examples"

if [ -z $PYTHONPATH ]; then
  export PYTHONPATH="${DAVE_INST_DIR}:$PYTHONPATH"
else
  export PYTHONPATH="${DAVE_INST_DIR}"
fi

export PATH="${DAVE_INST_DIR}/bin:${mPROBO_DIR}/bin:${mGENERO_DIR}/bin:${mLINGUA_DIR}/bin:$PATH"

# Load anaconda environment 
export PYTHONHOME="$HOME/anaconda2/envs/dave"
if [ -z $LD_LIBRARY_PATH ]; then
  export LD_LIBRARY_PATH="${PYTHONHOME}/lib:${LD_LIBRARY_PATH}"
else 
  export LD_LIBRARY_PATH="${PYTHONHOME}/lib"
fi

export PATH="${PYTHONHOME}/bin:$PATH"
