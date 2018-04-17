#!/bin/csh -f
# 1. Environment variables needed to be set
#   - mLingua_INST_DIR : root directory of PWL generation project
#   - PYTHONPATH : Append mLingua_INST_DIR to PYTHONPATH
# 2. Append ${mLingua_INST_DIR}/bin to your path
# 3. Load appropriate environment for running Synopsys VCS(-MX)

setenv mLINGUA_DIR /home/bclim/proj/modeling/pwlgen

if ( $?PYTHONPATH ) then
  setenv PYTHONPATH ${mLingua_INST_DIR}:$PYTHONPATH
else
  setenv PYTHONPATH ${mLingua_INST_DIR}
endif

set path = ($path ${mLingua_INST_DIR}/bin)

module load base 
if (`hostname` == "bclim-laptop") then
  module load vcs/H-2013.06-SP1
else
  module load vcs/H-2013.06
endif
#module load hspice
source ~/proj/mcktbook/setup.cshrc
