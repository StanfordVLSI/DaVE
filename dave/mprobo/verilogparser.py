#

__doc__ = '''
Limited verilog parser for module instantiation statement
'''

import re
import StringIO
import os
import dave.mprobo.mchkmsg as mcode

verilog_keyword_no_semicolon = ["`include","`define","`timescale","`ifdef","`endif","`else", "end", "begin", "initial", "always"]

def _commentstripper(txt, delim):
  'Strips first nest of block comments'
  deliml, delimr = delim
  out = ''
  if deliml in txt:
    indx = txt.index(deliml)
    out += txt[:indx]
    txt = txt[indx+len(deliml):]
    assert delimr in txt, mcode.ERR_009 + txt
    indx = txt.index(delimr)
    out += txt[(indx+len(delimr)):]
  else:
    out = txt
  return out

def strip_verilog_blockcomments(txt, delim=('/*', '*/')):
  'Strips nests of block comments'
  deliml, delimr = delim
  while deliml in txt:
    txt = _commentstripper(txt, delim)
  return txt

def strip_verilog_comments(line, begin_char):
  """ strip comments denoted by the character, begin_char """
  for mobj in re.finditer(begin_char+r".*$|'[^']*'"+r'|"[^"]*"', line):
    sp = mobj.span()
    if line[sp[0]] not in ["'", '"']:
      line = line[:sp[0]] + line[sp[1]:]
  return line

def find_cell_parameter(line):
  ''' In Verilog instantiation statement,
      extract parameter mapping part
  '''
  _tmp = re.split('#\s*\(', re.split('\)\s*\w+\s*\(', line)[0])
  if len(_tmp) == 2 and _tmp[-1].count('(')==_tmp[-1].count(')'):
    return re.sub(r'\s*', '',_tmp[-1])
  else:
    return None

def find_cell_master(line):
  ''' In Verilog instantiation statement,
      get cell name
  '''
  matched = re.findall('\w+',re.findall('^([^\s]*)',line.lstrip())[0])
  if len(matched) > 0:
    return matched[0]
  else:
    return None

def find_inst_name_and_port_map(line, cellname, parameter):
  ''' for given line, cell name & parameters
      find out 
        - instance name
        - port mapping 
      If it is successful, return tuple of (instance name, port mapping)
      Otherwise, return None
  '''
  line = line.rstrip('\n')
  if parameter != None: # if parameter instantiation exists
    instname = re.sub('\s*\($','',re.sub('^\)\s*','',re.findall('\)\s*\w+\s*\(', line)[0]))
    #_tmp = re.split('#\s*\(', re.split('\)\s*\w+\s*\(', line)[1])
    _tmp = re.split('\)\s*\w+\s*\(', line)[1]
  else:
    instname = re.split('\s*\(',re.sub('^\s*%s\s*' % cellname, '', line))[0]
    _tmp = re.sub('^\s*%s\s*%s\s*\(' %(cellname, instname), '', line)

  portmap = re.sub('\)\s*;','', _tmp)
  portmap = re.sub(r'\)\)',')', re.sub(r'\s*','',portmap))
  portmap = portmap.lstrip()
  if portmap.count('(') == portmap.count(')'):
    return instname, portmap
  else:
    return None

def parse_instance(line):
  ''' parse instantiation statement 
  '''
  if len(line)>0:
    line = strip_verilog_comments(line,'\/\/')
    cellname = find_cell_master(line)
    parameter = find_cell_parameter(line)
  
    _tmp = find_inst_name_and_port_map(line, cellname, parameter)
  
    if _tmp != None and cellname != None and _tmp[1] != None:
      return cellname, parameter, _tmp[0], _tmp[1]
    else:
      return None
  else:
    return None

def is_instance(line):
  ''' check if line is instantiation statement '''
  i = parse_instance(line)
  if i != None:
    return True if len(i)==4 else False
  else:
    return False

def parse_parameter(line):
  ''' parse if the statement is parameter '''
  line = strip_verilog_comments(line,'\/\/')
  line.strip()
  if line.split()[0]=='parameter':  # the line is parameter definition
    fields = line.split('=')
    param = fields[0].split()[-1]
    pvalue = fields[1].split()[0].rstrip(';')
    if fields[1].split()[0] == pvalue+';':
      p_rest = ';'
    else:
      p_rest = ' '.join(fields[1].split()[1:])
    return True,param,pvalue,p_rest
  return False,'','',''

def parse_port_map(line, logger=None):
  ''' parse Verilog port mapping (port by name) statement 
      it returns a dict 
        - key: port name
        - value: wire name
  '''
  instance = parse_instance(line)
  if instance != None:
    portmap = re.sub(r'\s+', '', instance[3])
    statement = re.sub(r'\s+', '', portmap)
    port=re.split(',',statement)
    try:
      return dict([(re.findall('\.(\S*)\(',p)[0], re.findall('\(([^\)]*)',p)[0]) for p in port])
    except:
      if logger != None:
        logger.debug('Errors in parsing port map (%s), since parsing Verilog netlist is not fully supported yet' % line)
      else:
        print 'Errors in parsing port map (%s), since parsing Verilog netlist is not fully supported yet' % line
      return None
  else:
    return None

def getline_verilog(filename, stringio=False):
  ''' get a single line from a verilog netlist
  '''
  if stringio:
    infile = filename
  else:
    try: infile = open(filename,'r')
    except: raise IOError(mcode.ERR_010 % filename)

  txt = ''
  for l in infile:
    txt += l
  txt = strip_verilog_blockcomments(txt)
  txt = strip_verilog_blockcomments(txt,('(*','*)')) # in caes the model is created using amsdirect, amsdesigner in Cadence
  
  _vlogfile = StringIO.StringIO()
  _vlogfile.write(txt)

  tline = ''
  for line in _vlogfile.getvalue().splitlines():
    line = strip_verilog_comments(line,'\/\/')
    line = line.strip()
    try:
      if ';' in line or line.split()[0].strip() in verilog_keyword_no_semicolon:
        yield tline+' '+line+'\n'
        tline = ''
      else:
        tline += ' '+line
    except:
      continue
  infile.close()
  yield tline+'\n'

def get_port(filename, modulename):
  ''' read a verilog file and extract list of ports in a module
  '''
  vlog = getline_verilog(filename)
  prefix = 'module %s ' % modulename
  for l in vlog:
    l = l.lstrip(' ')
    
    if l.startswith(prefix): 
      port_str = l.lstrip(prefix).replace('(','').replace(')','').replace(';','').rstrip('\n').rstrip(' ').split(',')
      ports = [p.strip().split()[-1] if ' ' in p.strip() else p.strip() for p in port_str]
  return ports

def build_parameter(para={}):
  ''' build a verilog parameter map string '''
  strout = ''
  return ', '.join(['.%s(%s)' % (p,v) for p, v in para.items()])

def buildline_verilog(cellname, parameter, instname, portmap):
  if parameter == None:
    return ' '.join([cellname,instname,'('+portmap+');'])
  else:
    return ' '.join([cellname,'#('+parameter+')',instname,'('+portmap+');'])

def putline_verilog(dst_file, netlist_str):
  dst_file.write(netlist_str+'\n')

def get_tb_port(parameter):
  ''' get mProbo port names from a Verilog testbench (starts with @)
  '''
  port=re.split(',',parameter)
  value = [re.findall('\(([^\)]*)',p)[0] for p in port]
  return [v.lstrip('@') for v in value if v.startswith('@')]
