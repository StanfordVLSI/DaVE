__doc__ = '''
  Extract wires from a Verilog testbench to minimize [wire] section effort
'''

import os
import re
import StringIO
from dave.mprobo.environ import EnvFileLoc
import dave.mprobo.verilogparser as vp
from dave.common.primitive import WireCrossReference 
from dave.common.davelogger import DaVELogger


#--------------------------------------------------------------------------------
class TestBenchWire(object):
  ''' Extract Wire Information 
      This will return a tuple of 
        - multiline testbench string 
        - list of variable port; input ports to a system being checked
  '''

  def __init__(self, pref_filename, vlog_tb='', logger_id='logger_id'):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    _envfile = EnvFileLoc()
    if vlog_tb != '':
      self.load_testbench(vlog_tb)
    self._pref = WireCrossReference(pref_filename) # port reference class obj.

  def load_testbench(self, vlog_tb):
    ''' Load Verilog testbench and build wire map
    '''
    vlog_lines = self._load(vlog_tb) # load raw testbench body
    self._tb_body, self._tb_port, inst_port, bus = self._parse_vlogtb(vlog_lines) # parse raw testbench body
    self._wires, self._unresolved_wires = self._build_wires(inst_port, bus)

  def get_wires(self): # return wire (resolved and unresolved) map
    return self._wires, self._unresolved_wires

  def get_testbench_port(self): # return testbench(mprobo) port
    return self._tb_port

  def get_testbench(self):  # build/return multiline testbench with wire declaration
    _vlog_tb = StringIO.StringIO()
    for w, v in self._wires.items()+self._unresolved_wires.items():
      for n in v:
        _vlog_tb.write("`%s %s" %(w,n)+'\n')
    _vlog_tb.write('\n')
    for l in self._tb_body:
      _vlog_tb.write(l+'\n')
    return _vlog_tb.getvalue()

  def _load(self, vlog_tb):
    ''' load verilog testbench in multiline text and return Verilog lines for parsing it.  '''
    vlog_file = StringIO.StringIO(vlog_tb)
    return vp.getline_verilog(vlog_file, stringio=True)

  def _parse_vlogtb(self, vlog_lines):
    ''' parse verilog lines to extract testbench(mprobo) ports (tb_port), port map, busified net (bus_net)
    '''
    tb_body = [] # testbench body
    tb_port = [] # mProbo port 
    inst_port  = [] # List of port map (dict of port and its wire) of each instance
    bus = {} # Busified net (key is bus name, value is tuple of msb and lsb)
    for l in vlog_lines:
      inst = vp.parse_instance(l)
      if inst != None:
        _line = vp.buildline_verilog(*inst)
        _line = _line.replace('^cds_globals.','@').replace('\\','')
        tb_body.append(_line)
        _pmap = vp.parse_port_map(_line, self._logger) # dict of port and its wire for each instance
        if _pmap != None:
          inst_port.append((inst[0], _pmap)) # append the port map to port_map
          bus = self._get_bus_size(_pmap.values(), bus) # create busified nets if any
          if inst[1] != None:
            tb_port += vp.get_tb_port(vp.find_cell_parameter(_line)) # extract mProbo port in a Verilog instance parameter
    return tb_body, tb_port, inst_port, bus
  
  def _get_bus_size(self, nets, bus):
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
        if name in bus.keys():
          bus.update({name:(max(msb,bus[name][0]), min(lsb, bus[name][1]))})
        else:
          bus.update({name:(msb, lsb)})
  
    return bus
  
  def _is_bus(self, net, bus):
    ''' check if net is a (subset of) bus 
        if not, return the original net value,
        if it is, return the net name after stripping off [\d+:\d+]
    '''
    for k in bus.keys():
      if net.startswith(k+'['):
        return True, k
    return False, net
  
  def _build_wires(self, inst_port, bus_net):
    ''' build wire declaration in testbench '''
    discipline = dict([(d, []) for d in self._pref.get_all_wiretype()])
    net_yet_resolved = [] # port discipline is NOT defined in port reference
    net_resolved = []     # port discipline is not defined in port reference

    for inst in inst_port: # for each instance
      for k in inst[1].keys(): # port
        d = self._pref.get_wiretype(inst[0], k)
        net = inst[1][k] # net
        if d != None: # if signal is defined in xref file
          _isbus, netname = self._is_bus(net, bus_net)
          net_resolved.append(netname)
          discipline[d].append(netname)
        else: # if discipline is not yet resolved
          _isbus, netname = self._is_bus(net, bus_net)
          net_yet_resolved.append(netname)
    
    net_yet_resolved = list(set(net_yet_resolved)-set(net_resolved))

    for k, v in discipline.items(): # get rid of duplicates and sort 
      discipline[k] = sorted(list(set(v)))
  
    unresolved_discipline = {self._pref.get_default_wiretype(): sorted(list(set(net_yet_resolved)))} # unresolved net is set to default_wiretype 
    
    wires = self._busify_net(discipline, bus_net)
    unresolved_wires = self._busify_net(unresolved_discipline, bus_net)
    if len(net_yet_resolved) > 0:
      self._logger.debug('There are some unresolved nets')
    return wires, unresolved_wires 
  
  
  def _busify_net(self, discipline, bus_net): # busify net if any
    # build Verilog statements of wire declaration
    _dis = {}
    for k,v in discipline.items():
      _dis[k] = ['[%d:%d] %s' %(bus_net[n][0], bus_net[n][1], n) if n in bus_net.keys() else n for n in v]
    return _dis
      
#      for n in v:
#        if n in bus_net.keys():
#          busify = ' [%d:%d]' %(bus_net[n][0], bus_net[n][1])
#        else:
#          busify = ''
#    
#        yield '`%s%s %s;' %(k, busify, n);
  
'''
def main():
  pref_filename = os.path.join(os.environ['DAVE_SAMPLES'], 'mProbo', 'port_xref.cfg')
  body = """
// Because of sanity check, it is suggested to use [[[wire]]] section than directly declaring in the tb_code
//`pwl avdd, gnd, v0, v1, vout;
//`logic sel0;
//`amsgnd(gnd)

amux dut ( .avdd(avdd), .avss(gnd), .sel0(sel0), .i0(v0), .i1(v1), .out(vout)); // device under test
vdc #(.dc(@avdd) ) xavdd ( .vout(avdd) );  // dc voltage source in PWL datatype
vdc #(.dc(@v0) ) xv0 ( .vout(v0[4:2]) );
vdc #(.dc(@v1) ) xv1 ( .vout(v1) );
bitvector #( .value(@sel0), .bit_width(1) ) xsel0 ( .out(sel0) ); // bit vector
// sample/dump the response "vout" defined as analog output in [[port]] section
// note that the filename has a prefix of "meas_" followed by its output port name "vout", and a file extension ".txt"
strobe_ss #(.ts(0), .ti(1e-9), .tol(0.001), .filename("meas_vout.txt")) xstrobe (.in(vout), .detect(ss_detect));
finish_sim xfinish(.in(ss_detect));
"""
  t = TestBenchWire(pref_filename)
  t.load_testbench(body)
  print t.get_testbench()
  print t.get_wires()
  print t.get_testbench_port()

if __name__=="__main__":
  main()
'''
