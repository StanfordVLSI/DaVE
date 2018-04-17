# Server class for server-client mode

import socket
import time
import os
import threading
import signal
from dave.common.davelogger import DaVELogger
from dave.common.misc import make_dir, get_dirname
from dave.mprobo.environ import EnvFileLoc

#----------------------------------
class mProboServer(object):
  ''' 
  Class for mProbo Server
  '''
  _CMD = {
    'upload': '@upload', # upload files from a client to the server
    'download': '@download', # download files from the server to a client
    'run_verilog': '@run_verilog', # request for running Verilog simulations under X directory
    'run_pp': '@run_pp', # request for running post-processing routines under X directory
    'pp_list': '@pp_list', # list of post-processing scripts to be sent to a client
    'connect': '@connect', # inform connected
    'invalid_user': '@invalid_user', # notify invalid user
    'max_license': '@max_license', # connection closed because max license reached
    'close': '@close', # close client socket
    'dummy': '@dummy', # dummy command
  }
  _BUFSIZ = 1024
  _TIME_SLEEP = 0.5

  def __init__(self, conn, workdir, addr, logger_id):
    self._logger = DaVELogger.get_logger('%s.%s.%s' % (logger_id, __name__, self.__class__.__name__)) # logger
    self._workdir = workdir # mProbo working directory on server side
    self._csocket = conn
    self.clear_command()
    # run wait_for_command in background
    self._thread = threading.Thread(target=self.wait_for_command, args=())
    self._thread.daemon = True
    self._thread.start()

  def get_workdir(self):
    ''' Return working directory '''
    return self._workdir

  def issue_command(self, cmd=''):
    ''' Issue a command 
        Issuing a command need a real command followed by a dummy command
    '''
    self._issue_command(cmd)
    self._issue_command('@dummy')

  def _issue_command(self, cmd=''):
    ''' Issue a command without dummy '''
    while self._command != '':
      continue
    self._command = cmd
    
  def clear_command(self):
    ''' Clear command '''
    self._command = ''

  def wait_for_command(self):
    ''' Wait for a command '''
    while True:
      data = self._command
      if data.startswith(self._CMD['download']): # request download 
        self.download(data)
      elif data.startswith(self._CMD['upload']): # request upload
        self.upload(data)
      elif data.startswith(self._CMD['run_verilog']): # request verilog run
        self.run_verilog(data)
      elif data.startswith(self._CMD['run_pp']): # request post-processor run
        self.run_pp(data)
      elif data.startswith(self._CMD['pp_list']): # request post-processor run
        self.send_pp_list(data)
      elif data.startswith(self._CMD['connect']): # inform connection
        self.inform_connected(data)
      elif data.startswith(self._CMD['invalid_user']): # inform invalid connection
        self.inform_invalid(data)
      elif data.startswith(self._CMD['max_license']): # inform max license reached
        self.inform_max_license(data)
      elif data.startswith(self._CMD['close']): # close socket
        break
      elif data.startswith(self._CMD['dummy']): # dummy command
        self.clear_command()
        continue
      time.sleep(self._TIME_SLEEP/10.0)
    self.close(data)
      
  def inform_connected(self, data):
    ''' Inform a client that it is connected '''
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()

  def inform_invalid(self, data):
    ''' Inform a client that the client IP is not registered for use '''
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()

  def inform_max_license(self, data):
    ''' Inform a client that the # of licenses for this client IP is reached '''
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()
          
  def run_verilog(self, data):
    ''' Let a client run verilog simulation '''
    self._logger.debug("[SIMULATION] Request running Verilog simulation")
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()

  def send_pp_list(self, data):
    ''' Send a list of post-processing script files to a client before running the pp'''
    self._logger.debug("[SIMULATION] Sending list of post-processing script files")
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()

  def run_pp(self, data):
    ''' Let a client run post-processing routines '''
    self._logger.debug("[SIMULATION] Request running post-processing routine")
    self._csocket.send(data)
    time.sleep(self._TIME_SLEEP)
    self.clear_command()

  def upload(self, data):
    ''' Receive files from a client '''
    mprobo_rundir = EnvFileLoc().root_rundir
    files = data[len(self._CMD['upload'])+1:].split()
    files = [f[f.rfind('%s'%mprobo_rundir):] if f.rfind('%s'%mprobo_rundir)>=0 else f for f in files]
    new_data = ' '.join([self._CMD['upload']]+files)
    self._csocket.send(new_data)
    for f in files:
      self._fileC2S(f)
    self.clear_command()

  def download(self, data):
    ''' Send files to a client '''
    self._csocket.send(data)
    for f in data[len(self._CMD['download'])+1:].split():
      self._fileS2C(f)
    self.clear_command()

  def close(self, data):
    ''' Close client socket '''
    self._csocket.send(data)
    self._csocket.close()
    self.clear_command()

  def _fileC2S(self, filename):
    ''' Receive a file from a client '''
    full_path = os.path.abspath(os.path.join(self._workdir, filename))

    self._logger.debug("[FILE] Client->Server: %s" % full_path)
    time.sleep(self._TIME_SLEEP)
    
    dirname = get_dirname(full_path)
    make_dir(dirname, self._logger)
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
  
  def _fileS2C(self, filename) :
    ''' Send a file to a client '''

    full_path = os.path.join(self._workdir, filename)
  
    self._logger.debug("[FILE] Server->Client: %s" % full_path)

    while not os.path.exists(full_path): # wait for file creation
      self._logger.debug("[FILE] The file %s is not created yet. Will be waiting for another %d seconds" % (full_path, self._TIME_SLEEP))
      time.sleep(self._TIME_SLEEP)

    time.sleep(self._TIME_SLEEP)
      
    f = open(full_path,'rb')
    while True:
      data = f.read()
      if data=='':
        time.sleep(self._TIME_SLEEP)
        self._csocket.sendall("[@EOF]")  
        break
      else :
        self._csocket.sendall(data)
    f.close() 
