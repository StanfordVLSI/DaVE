#!/usr/bin/env python

# Client program of mProbo in server-client mode

import socket
import time
import os
import sys
import logging
import tempfile
import stat
import shutil
import subprocess
import signal
import argparse
import copy
import re
import random
import string

logger_prefix = 'mProbo_logger'
client_logfile = 'mProbo_client.log'
client_runarg_file = 'runargs.txt'
simlogfile = 'mProbo_sim.log'

logging.basicConfig(filename=".mProbo_client.log", filemode='w', level=logging.INFO)
logger = logging.getLogger(logger_prefix)
ch = logging.StreamHandler(sys.stdout)
ch1 = logging.StreamHandler(open(client_logfile,"w"))
ch.setLevel(logging.INFO)
ch1.setLevel(logging.INFO)
logger.addHandler(ch)
logger.addHandler(ch1)

def interpolate_env(value):
  ''' interpolate environment variable if exist '''
  newvalue = copy.deepcopy(value)
  envs = re.findall('\$\{\w+\}', value)
  for e in envs:
    evar = e.strip("$").strip("{").strip("}")
    try:
      newvalue = newvalue.replace(e, os.environ[evar])
    except:
      print "Environement variable (%s) does not exist !!!" % evar
  return newvalue

def preprocess_cfg(cfg_filename, suffix='_pp'):
  dirname, basename = os.path.split(os.path.abspath(cfg_filename))
  rootname, extname = os.path.splitext(basename)
  fid = open(os.path.join(dirname, rootname+suffix+extname), 'w')
  with open(cfg_filename, 'r') as f:
    for l in f.readlines():
      fid.write(interpolate_env(l))
  fid.close()

def pass_args():
  ''' process shell command args '''
  
  rpt_filename = 'report.html'
  parser = argparse.ArgumentParser(description='mProbo client program')
  parser.add_argument('-x','--extract', action='store_true', help='Extraction mode: Characterize golden model.')
  parser.add_argument('-r', '--rpt', help='Report file name in HTML format. Default is "%s"' % rpt_filename, default=rpt_filename)
  parser.add_argument('-p', '--port', help="Port in server/client mode", type=int, default=5000)
  parser.add_argument('-s', '--server', help="Server hostname in server/client mode", default="bclim-desktop.stanford.edu")
  return parser

def make_dir(dirname, logger=None, force=False):
  ''' 
  Make a directory. Return True if it is created 
  If force is True and the directory already exists, this will force to create the directory after renaming the existing one to a directory with a random suffix.
  '''
  if not os.path.exists(dirname):
    os.system('mkdir -p %s' % dirname)
    if logger: logger.debug('A directory %s is created.' % dirname)
    return True
  else:
    if logger: logger.debug('Directory %s alreayd exists.' % dirname)
    if force:
      old_dirname = dirname + generate_random_str('_old_', 5)
      os.rename(dirname, old_dirname)
      os.system('mkdir -p %s' % dirname)
      if logger:
        logger.debug('The existing directory is renamed to %s.' % old_dirname)
        logger.debug('A directory %s is created.' % dirname)
      return True
    return False

def get_dirname(filename):
  (dirname,basename) = os.path.split(os.path.abspath(filename))
  return dirname

def rmfile(filename):
  if os.path.isfile(filename):
    os.remove(filename)

def generate_random_str(prefix,N):
  char_set = string.ascii_uppercase + string.digits
  return prefix+''.join(random.sample(char_set,N-1))

#----------------------------------
class mProboClient(object):
  ''' 
  Class for mProbo Server
  '''
  _CMD = {
    'upload': '@upload',
    'download': '@download', # download a file from the server to a client
    'connect': '@connect',
    'run_verilog': '@run_verilog', # run Verilog simulations under X directory
    'run_pp': '@run_pp', # run post-processing rouine under X directory
    'pp_list': '@pp_list', # list of pp script files
    'invalid_user': '@invalid_user', # user validation failed
    'max_license': '@max_license', # connection closed because max license reached
    'close': '@close', # close client socket
  }
  _BUFSIZ = 1024
  _TIMEOUT_FILE = 60
  _TIME_SLEEP = 0.5
  _RUNARG_FILE = client_runarg_file

  def __init__(self, rundir, runargs, host, port):
    self._HOST = host
    self._PORT = port
    self._ADDR = (self._HOST, self._PORT)
    signal.signal(signal.SIGINT, self.sigint_handler)
    self._logger = logging.getLogger('%s.%s.%s' % (logger_prefix, __name__, self.__class__.__name__)) # logger
    self._rundir = rundir
    self._write_runargs(runargs)
    self._csocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connect()
    self.wait_for_command()

  def _write_runargs(self, runargs):
    ''' write run arguments string to a file '''
    with open(self._RUNARG_FILE, 'w') as f:
      f.write(runargs)

  def _delete_tempfiles(self):
    rmfile(self._RUNARG_FILE)
    rmfile('test_pp.cfg')
    rmfile('sim_pp.cfg')
      
  def get_rundir(self):
    return self._rundir

  def connect(self):
    self._csocket.connect((socket.gethostbyname(self._HOST),self._PORT))

  def wait_for_command(self):
    ''' wait for commands '''
    while True:
      data = self._csocket.recv(self._BUFSIZ)
      if data.startswith(self._CMD['download']):
        self.download(data)
      elif data.startswith(self._CMD['upload']): # download mode
        self.upload(data)
      elif data.startswith(self._CMD['run_verilog']): # wait for client mode
        self.run_verilog(data)
      elif data.startswith(self._CMD['pp_list']): #
        self.receive_pp_list(data)
      elif data.startswith(self._CMD['run_pp']): # wait for client mode
        self.run_pp(data)
      elif data.startswith(self._CMD['connect']): # wait for client mode
        self.inform_connected()
      elif data.startswith(self._CMD['invalid_user']): # wait for client mode
        self.inform_invalid(data)
      elif data.startswith(self._CMD['max_license']): # wait for client mode
        self.inform_max_license(data)
      elif data.startswith(self._CMD['close']): # wait for client mode
        break
    self.close()
          
  def run_verilog(self, data):
    ''' run verilog simulation under the directory '''
    dirname = data[len(self._CMD['run_verilog'])+1:]
    self._logger.info("[SIMULATION] Running Verilog simulation under %s" % dirname)
    run_script = './run_vlog.csh'
    cwd = os.getcwd()
    os.chdir(dirname)
    os.chmod(run_script, stat.S_IEXEC | stat.S_IREAD | stat.S_IWRITE)
    p=subprocess.Popen(run_script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err  = p.communicate()
    sim_msg = out + '\n' + err
    with open(simlogfile,'w') as f:
      f.writelines(sim_msg)
    os.chdir(cwd)

  def receive_pp_list(self, data):
    ''' receive list of post-processing script files '''
    self._logger.info("[SIMULATION] Receiving list of post-processing script files")
    self._pp_script = data[len(self._CMD['pp_list'])+1:].split()

  def run_pp(self, data):
    ''' run post-processing routine under the directory '''
    d = data[len(self._CMD['run_pp'])+1:].split()
    dirname = d[0]
    run_script = ' '.join(d[1:])
    self._logger.info("[SIMULATION] Running post-processing routine under %s" % dirname)
    cwd = os.getcwd()
    for f in self._pp_script:
      shutil.copy(f, dirname)
    os.chdir(dirname)
    p=subprocess.Popen(run_script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err  = p.communicate()
    sim_msg = out + '\n' + err
    with open(simlogfile,'w+') as f:
      f.writelines(sim_msg)
    os.chdir(cwd)

  def inform_connected(self):
    ''' show that this client is connected to the server '''
    self._logger.info("[CONN] Connected to the server, %s" % self._HOST)

  def inform_invalid(self, data):
    ''' show that this connection is invalid '''
    self._logger.info(data[len(self._CMD["invalid_user"])+1:])

  def inform_max_license(self, data):
    ''' show that max connection for this client is reached '''
    self._logger.info(data[len(self._CMD["max_license"])+1:])

  def upload(self, data):
    ''' Send files from a client to the server '''
    for f in data[len(self._CMD['upload'])+1:].split():
      self._fileC2S(f)

  def download(self, data):
    ''' Send files from the server to a client '''
    for f in data[len(self._CMD['download'])+1:].split():
      self._fileS2C(f)

  def close(self):
    ''' close client socket '''
    self._logger.info("[CONN] Close socket")
    self._csocket.close()
    self._delete_tempfiles()

  def _fileS2C(self, filename):
    ''' Receive a file from the server '''
    self._logger.info("[FILE] Server->Client: %s" % filename)
    time.sleep(self._TIME_SLEEP)
    
    full_path = os.path.join(self._rundir, filename)
    dirname = get_dirname(full_path)
    make_dir(dirname, self._logger, False)
    f = open(full_path,'wb')
    while True:
      data = self._csocket.recv(self._BUFSIZ)
      if data.find('[@EOF]') >=0 :
        break
      else :
        f.write(data)
    f.close()
    while not os.path.exists(full_path):
      continue

  
  def _fileC2S(self, filename) :
    ''' Send a file from a client to the server '''
    self._logger.info("[FILE] Client->Server: %s" % filename)

    full_path = os.path.join(self._rundir, filename)

    while not os.path.exists(full_path): # wait for file creation
      self._logger.info("[FILE] The file %s is not created yet. Will be waiting for another %d seconds" % (full_path, self._TIME_SLEEP))
      time.sleep(self._TIME_SLEEP)

    time.sleep(self._TIME_SLEEP)
      
    f = open(full_path,'rb')
    while True:
      data = f.read()
      if data=='':
        time.sleep(self._TIME_SLEEP)
        self._csocket.send("[@EOF]")  
        break
      else:
        self._csocket.send(data)
    self._logger.info("[INFO] Finish Client->Server: %s" % filename)
    f.close() 

  def sigint_handler(self, signal, frame):
    print "The program is interrupted by user. Terminate the program abnormally."
    self.close()
    sys.exit(0)

def main(args):
  make_str = lambda k,v: k if type(v)==type(True) and v else '' if type(v)==type(True) else '--'+k+' '+v
  host = args.server
  port = args.port
  args_dict = vars(args)
  del args_dict['server']
  del args_dict['port']
  arg_str = ' '.join([make_str(k,v) for k,v in vars(args).items()])
  mc = mProboClient(os.getcwd(), arg_str, host, port)

if __name__=="__main__":
  args = pass_args().parse_args()
  preprocess_cfg('test.cfg')
  preprocess_cfg('sim.cfg')
  main(args)
