import glob
from dave.common.empyinterface import EmpyInterface

template = "oa_module.empy"
output_filename = "oatable.py"

param = {'table': {}}

for f in glob.glob("*.tbl"):
  with open(f, 'r') as fid:
    content = fid.read().strip('\n')
    param['table'][f.replace(".","_")]=content
EmpyInterface(output_filename)(template, param)

