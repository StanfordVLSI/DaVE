#!/usr/bin/env python
# Server class for server-client mode

import socket
import time
import os
import sys
import thread
import tempfile
import logging
import subprocess
import shutil
import fnmatch 
import argparse
import signal
from time import strftime, localtime
from dave.common.davelogger import DaVELogger
from dave.common.misc import rmfile, make_dir, assert_file
from dave.common.netstat import get_established_foreign_ip_address
from dave.mprobo.environ import EnvRunArg, EnvFileLoc, EnvMisc
from dave.mprobo.server import mProboServer
from dave.mprobo.launcher import launch, pass_args

#----------------------------------
# creating logger
logger_id = EnvMisc().logger_prefix+'_server'
logging.basicConfig(filename=EnvFileLoc().server_logfile,
                    filemode='w',
                    level=logging.DEBUG)
logger = logging.getLogger(logger_id)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

#----------------------------------
def pass_args_server():
  ''' process shell command args for mProbo_server '''
  def_userfile = os.path.join(os.environ['DAVE_INST_DIR'],EnvFileLoc().server_userfile)
  def_no_clients = EnvMisc().no_clients
  def_port = int(EnvMisc().server_port)
  parser = argparse.ArgumentParser(description='Launch mProbo server application')
  parser.add_argument('-u', '--user', help='User IP registration file. The default is "%s".' % def_userfile, default=def_userfile)
  parser.add_argument('-n', '--number', help='Number of clients. The default is "%s".' % def_no_clients, default=def_no_clients)
  parser.add_argument('-p', '--port', help="Port in server/client mode. The default is %d." % def_port, type=int, default=def_port)
  return parser

#----------------------------------
class mProboServerLauncher(object):
  ''' Server Launcher '''
  _HOST = ''
  _TIMEOUT = 60
  def __init__(self, args):
    signal.signal(signal.SIGINT, self.sigint_handler)
    self._ur_filename = args.user
    self._NO_CLIENTS = int(args.number)
    self._PORT = int(args.port)
    self._ADDR = (self._HOST, self._PORT)
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #self._ssocket.settimeout(self._TIMEOUT)
    self._ssocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reuse the socket immediately
    self._ssocket.bind(self._ADDR) # bind socket to the address
    self._ssocket.listen(self._NO_CLIENTS) # start listening. limit the number of clients being connected
    self._print_setting()
    self._logger.info("TCPServer Waiting for client on port %d" % self._PORT)
    self.connect()

  def _print_setting(self):
    t = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    self._logger.info("")
    self._logger.info("="*55)
    self._logger.info("* mProbo_server starts at %s" % t)
    self._logger.info("* Hostname: %s" % socket.gethostname())
    self._logger.info("* Port: %s" % self._PORT)
    self._logger.info("* # of clients: %d" % self._NO_CLIENTS)
    self._logger.info("="*55)
    self._logger.info("")

  def connect(self):
    ''' Bring up server '''
    while True:
      conn, addr = self._ssocket.accept()
      thread.start_new_thread(self.spawn_client,(conn,addr))
    conn.close() # ensure closing clients
    self._ssocket.close()

  def spawn_client(self, conn, addr):
    ''' spawning client '''
    make_dir(EnvFileLoc().server_tempdir, self._logger) # make working directory
    workdir = tempfile.mkdtemp(prefix='%s_%s_' %(addr[0],addr[1]), dir=EnvFileLoc().server_tempdir)
    self._logger.info("Working directory is set to %s" % workdir)
    mProboRunServerMode(conn, workdir, addr, self._ur_filename, self._PORT)

  def sigint_handler(self, signal, frame):
    print "The program is interrupted by user. Terminate the program abnormally."
    self._ssocket.close()
    sys.exit(0)

#-------------------------
class mProboRunServerMode(object):

  _RUNARG_FILE = EnvFileLoc().client_runarg_file

  def __init__(self, conn, workdir, addr, ur_filename, port):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._server = mProboServer(conn, workdir, addr, logger_id) # make communication channel
    self._addr = addr
    self._workdir = workdir
    self.check_connection()
    is_valid, no_acct, company = self.validate_user(addr[0], ur_filename)
    t = strftime("%a, %d %b %Y %H:%M:%S", localtime())
    self._logger.info("[CONN] Got a connection from %s (%s) at %s" % (str(addr), company, t) )
    if is_valid:
      fn_match_ip = lambda x: x==addr[0]
      ip_addrs = filter(fn_match_ip, get_established_foreign_ip_address(port))
      no_runs =  len(ip_addrs)
      if no_runs <= no_acct:
        self.upload_configuration_files() # get test.cfg & sim.cfg
        self._runargs = self.get_runargs() # get args of mProbo
        self.run() # run mProbo
        self.send_result() # 
        self._logger.info("Temporary working directory: %s" % self._workdir)
      else:
        self._server.issue_command("@max_license [CONN] Maximum # of licenses for the IP (%s): %s reached. Connection closed" % (addr[0], no_acct))
        self._logger.info("[CONN] Maximum # of licenses for the IP (%s): %s reached. Connection closed" % (addr[0], no_acct))
    else:
      self._logger.info("[CONN] Invalid IP: %s. Connection closed" % addr[0])
    self.close_connection()
    #self.cleanup_workdir()
    thread.exit()

  def validate_user(self, ip_addr, ur_filename):
    is_valid = False
    with open(ur_filename, 'r') as f:
      for l in f.readlines():
        field = l.strip().split()
        if field[0].startswith('*'): continue
        if fnmatch.fnmatch(ip_addr, field[0]):
          return True, int(field[1]), field[2].replace('_', ' ')
    self._server.issue_command('@invalid_user User validation failed.')
    return False, 0, ''

  def check_connection(self):
    ''' Check connection '''
    self._server.issue_command('@connect') 

  def upload_configuration_files(self):
    ''' upload test/sim configuration files to the server '''
    #self._server.issue_command('@upload %s %s' % (EnvRunArg().testcfg_filename, EnvRunArg().simcfg_filename))
    self._server.issue_command('@upload %s %s %s' % ('test_pp.cfg', 'sim_pp.cfg', 'circuit.scs'))
    
  def get_runargs(self):
    ''' get mProbo run arguments'''
    self._server.issue_command('@upload %s' % self._RUNARG_FILE)
    argfile = os.path.join(self._workdir,self._RUNARG_FILE)
    with open(argfile,'r') as f:
      args = f.read()
    rmfile(argfile)
    #args = args + ' -w {wdir} -t {test} -s {sim}'.format(wdir=self._workdir,test=os.path.join(self._workdir,EnvRunArg().testcfg_filename), sim=os.path.join(self._workdir,EnvRunArg().simcfg_filename))
    args = args + ' -w {wdir} -t {test} -s {sim}'.format(wdir=self._workdir,test=os.path.join(self._workdir,'test_pp.cfg'), sim=os.path.join(self._workdir,'sim_pp.cfg'))
    return args.split()

  def run(self):
    ''' run mprobo '''
    self._logger.info("Run mProbo")
    args = pass_args().parse_args(self._runargs)
    self._rpt_filename = args.rpt
    launch(args, self._server)
  
  def send_result(self):
    self._server.issue_command('@download %s %s/extracted_linear_model.yaml %s' % (self._rpt_filename, EnvFileLoc().root_rundir, EnvFileLoc().logfile))

  def close_connection(self):
    ''' close connection '''
    self._server.issue_command('@close')
    self._logger.info("[CONN] Connection %s closed" % str(self._addr))
  
  def cleanup_workdir(self):
    ''' delete workdir '''
    shutil.rmtree(self._workdir)

def main():
  args = pass_args_server().parse_args()
  assert_file(args.user)
  mProboServerLauncher(args) #ur_filename, args.client)

if __name__ == "__main__":
  main()
