#!/bin/csh -f

R -f make_oa_table.R
python make_oa_module.py
cp oatable.py ../../
