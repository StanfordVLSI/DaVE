__doc__ = '''
  Generates Verilog(-AMS) testbench.
  This module also includes a class to interface with Cadence's Virtuso schematic capture
'''

import os
from environ import EnvFileLoc, EnvSimcfg, EnvTestcfgSection
from dave.common.empyinterface import EmpyInterface
from dave.common.davelogger import DaVELogger
import testbench_template
from dave.common.primitive import WireCrossReference 
import verilogparser as vp
import copy
import subprocess
import StringIO
import re
import dave.mprobo.mchkmsg as mcode

#-----------------------
class TestBench(object):
  ''' 
    There are two main functions:
      - to create an intermediate (raw) testbench from a testbench template in testbench_template.py.
      - to provide a method to bind testvectors to the intermediate testbench.
  '''


  def __init__(self, test_cfg, sim_cfg, workdir='/tmp', logger_id='logger_id'):
    ''' 
      This immediately generates a raw testbench file with the information in test/simulator configurations 
    '''
    envsim = EnvSimcfg()
    envtest = EnvTestcfgSection()

    self.tb_template = copy.deepcopy(testbench_template.tb_template)
    test = test_cfg.get_test()
    config_name = sim_cfg.get_config_name() # golden or revised
    model = sim_cfg.get_model() # ams or verilog
    ic = test_cfg.get_ic_golden() if sim_cfg.is_golden() else test_cfg.get_ic_revised()
    param ={ envsim.model : model, 
             envsim.simulator : sim_cfg.get_simulator_name(), 
             envsim.hdl_include_files : sim_cfg.get_hdl_include_files(),
             envtest.initial_condition : ic }
    param.update(test)

    filename = 'tb_%s_%s.v' % (test_cfg.get_test_name(), config_name)
    self._tb_raw = self.generate( self.tb_template, param, filename, workdir) 

  @classmethod
  def generate(cls, raw_tb_file, param, filename, workdir='/tmp'):
    ''' return a testbench file after binding testvectors (param) to the raw testbench file '''
    if type(raw_tb_file) == type(''):
      assert os.path.exists(raw_tb_file), mcode.ERR_020 % raw_tb_file
    return EmpyInterface(os.path.join(workdir, filename))(raw_tb_file, param)

  def get_raw_filename(self):
    ''' it returns raw testbench filename '''
    return self._tb_raw


#-----------------------------------
class TestBenchCDSInterface(object):
  ''' Interface with Cadence's Virtuso schematic to generate a testbench
      This will return a tuple of 
        - multiline testbench string 
        - list of variable port; input ports to a system being checked
  '''

  def __init__(self, logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    _envfile = EnvFileLoc()

  def __call__(self, cdslib_path, libname, cellname, viewname, pref_filename):
    ''' build a multiline testbench string in Verilog from Cadence's Virtuoso schematic database
    '''

    success, vlog_filename = self._create_cdsverilog(cdslib_path, libname, cellname, viewname)
    if success:
      lines = []
      tb_port = []
      tb_net  = []
      bus_net = {}
      for l in vp.getline_verilog(vlog_filename):
        inst = vp.parse_instance(l)
        if inst != None:
          newl = vp.buildline_verilog(*inst)
          newl = newl.replace('^cds_globals.','@').replace('\\','')
          lines.append(newl)
          portmap = vp.parse_port_map(newl)
          tb_net.append((inst[0],portmap))
          bus_net = self._get_bus_net(portmap.values(), bus_net)
          if inst[1] != None:
            tb_port += vp.get_tb_port(vp.find_cell_parameter(newl))
  
      wires = self._build_wires(tb_net, bus_net, pref_filename)
  
      _vlog_tb = StringIO.StringIO()
      for w in wires:
        _vlog_tb.write(w+'\n')
      _vlog_tb.write('\n')
      for l in lines:
        _vlog_tb.write(l+'\n')
  
      return _vlog_tb.getvalue(), tb_port
    else:
      return None


  def _get_bus_net(self, nets, bus_net):
    ''' build a dictionary of busified nets with MSB:LSB information
    '''
    for n in nets:
      b = re.findall('\[\d+:\d+]',n)
      if (b!=[]):
        b = b[0]
        name = n.replace(b,'')
        left = int(b.split(':')[0].replace('[',''))
        right = int(b.split(':')[1].replace(']',''))
        msb = max(left,right)
        lsb = min(left,right)
        if name in bus_net.keys():
          bus_net.update({name:(max(msb,bus_net[name][0]), min(lsb, bus_net[name][1]))})
        else:
          bus_net.update({name:(msb, lsb)})
  
    return bus_net
  
  def _is_bus(self, net, bus_net):
    ''' check if net is a (subset of) bus 
        if not, return the original net value,
        if it is, return the net name after stripping off [\d+:\d+]
    '''
    for k in bus_net.keys():
      if net.startswith(k+'['):
        return True, k
    return False, net
  
  def _build_wires(self, tb_net, bus_net, pref_filename):
    ''' build wire declaration in testbench '''
    pref = WireCrossReference(pref_filename)
    discipline = dict([(d, []) for d in pref.get_all_wiretype()])
    net_yet_resolved = []
    net_resolved = []
  
    for inst in tb_net: # for each instance
      for k in inst[1].keys(): # port
        d = pref.get_wiretype(inst[0], k)
        net = inst[1][k] # net
        if d != None: # if signal is defined in xref file
          _isbus, netname = self._is_bus(net, bus_net)
          net_resolved.append(netname)
          discipline[d].append(netname)
        else: # if discipline is not yet resolved
          _isbus, netname = self._is_bus(net, bus_net)
          net_yet_resolved.append(netname)
    
    net_yet_resolved = list(set(net_yet_resolved)-set(net_resolved))
  
    discipline[pref.get_default_wiretype()] += net_yet_resolved # unresolved net is set to default_wiretype 
  
    for k, v in discipline.items(): # get rid of duplicates and sort 
      discipline[k] = sorted(list(set(v)))
  
    # build Verilog statements of wire declaration
    for k,v in discipline.items():
      for n in v:
        if n in bus_net.keys():
          busify = ' [%d:%d]' %(bus_net[n][0], bus_net[n][1])
        else:
          busify = ''
        yield '`%s%s %s;' %(k, busify, n);
  
  def _create_cdsverilog(self, cdslib_path, libname, cellname, viewname):
    ''' generate verilog-ams of a testbench schematic 
        Then, use build_testbench_from_cdsverilog to generate mProbo testbench 
    '''
    cds_cmd = 'pushd ${{PWD}} > /dev/null\n cd {cdslib_path}\n amsdirect -lib {lib} -cell {cell} -view {view} -verilog\n popd'.format(lib=libname, cell=cellname, view=viewname, cdslib_path=cdslib_path)
    logmsg = os.path.join(cdslib_path, 'ams_direct.log')
    success = True
  
    filepath = os.path.join(cdslib_path, libname, cellname, viewname)
    verilog_filename = os.path.join(filepath, 'verilog.vams')
    if os.path.exists(verilog_filename): # delete if already exists
      os.remove(verilog_filename)
    if os.path.exists(logmsg): # delete if already exists
      os.remove(logmsg)
  
    p=subprocess.Popen(cds_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err  = p.communicate()
    sim_msg = out + '\n' + err
  
    success = os.path.exists(verilog_filename)
    msg = mcode.INFO_043 %('successful.' if success else mcode.INFO_044) 
    self._logger.info(msg)
    self._logger.info('='*len(msg))
    if not success:
      try:
        with open(logmsg, 'r') as f:
          for l in f.readlines():
            self._logger.info(l.strip('\n'))
      except:
        self._logger.warning(mcode.WARN_019)
  
    return success, verilog_filename
    

'''
def main():
  pref_filename = os.path.join(os.environ['DAVE_SAMPLES'], 'library', 'model', 'port_xref.cfg')
  tb = TestBenchCDSInterface()('/home/bclim/cktbook/opusdb', 'dave_prim', 'test2', 'schematic', pref_filename)
  if tb != None:
    print 'Testbench: '
    print ''
    print tb[0]
    print 'PORTS: ', tb[1]

if __name__=="__main__":
  main()
'''
