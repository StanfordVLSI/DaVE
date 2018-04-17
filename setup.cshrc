#!/bin/csh -f

# A sample setup file for DaVE

setenv DAVE_INST_DIR /home/bclim/proj/StanfordVLSI/DaVE
setenv DAVE_SAMPLES ${DAVE_INST_DIR}/samples

setenv mLINGUA_DIR ${DAVE_INST_DIR}/mLingua
setenv mLINGUA_DEMO_DIR ${mLINGUA_DIR}/examples
setenv mLINGUA_SIMULATOR ncsim  # vcs or ncsim
setenv mPROBO_DIR ${DAVE_INST_DIR}/mProbo
setenv mPROBO_DEMO_DIR ${mPROBO_DIR}/examples
setenv mGENERO_DIR ${DAVE_INST_DIR}/mGenero
setenv mGENERO_DEMO_DIR ${mGENERO_DIR}/examples

if ( $?PYTHONPATH ) then
  setenv PYTHONPATH ${DAVE_INST_DIR}:$PYTHONPATH
else
  setenv PYTHONPATH ${DAVE_INST_DIR}
endif

set path = ( ${DAVE_INST_DIR}/bin ${mPROBO_DIR}/bin ${mGENERO_DIR}/bin ${mLINGUA_DIR}/bin $path )

# Load anaconda environment 
setenv PYTHONHOME $HOME/anaconda2/envs/dave
if ( $?LD_LIBRARY_PATH ) then
  setenv LD_LIBRARY_PATH ${PYTHONHOME}/lib:${LD_LIBRARY_PATH}
else 
  setenv LD_LIBRARY_PATH ${PYTHONHOME}/lib
endif

set path = ( ${PYTHONHOME}/bin $path )

module load incisive vcs
