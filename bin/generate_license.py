# make a trial version s/w

import datetime
import hashlib
import random
import string
import StringIO
import os
import dave.mprobo.mchkmsg as mcode
import argparse

def pass_args():
  ''' process shell command arguments '''

  parser = argparse.ArgumentParser(description=mcode.INFO_002)
  parser.add_argument('-s','--server', help='License server name', default='localhost')
  parser.add_argument('-t', '--to', help='License goes to', default='Stanford_university')
  parser.add_argument('-d', '--duration', help='License duration from now on', type=int, default=365)
  parser.add_argument('-p','--probo', action='store_true', help='License mProbo')
  parser.add_argument('-l','--lingua', action='store_true', help='License mLingua')
  parser.add_argument('-g','--genero', action='store_true', help='License mGenero')
  return parser

args = pass_args().parse_args()

__license_duration__ = args.duration
server = args.server
license_to = args.to
__products__ = [('mProbo',args.probo), ('mLingua',args.lingua), ('mGenero',args.genero)]

__license_header__ = mcode.INFO_053
__license_server__ = 'SERVER={mid}'
__license_feature__ = 'PRODUCT_ID={pid} SN={sn} EXPR_DATE={expr} KEY={key}'
phrase = 'mcode.INFO_020'
salt = 'Ehdnsxmgor1!'
expiration = (datetime.date.today()+datetime.timedelta(__license_duration__)).strftime('%b-%d-%Y').lower()


def generate_sn(prefix, size=10,chars=string.ascii_lowercase+string.digits):
  return prefix+''.join(random.choice(chars) for _ in range(size))

def printToday():
  today = datetime.date.today()
  return datetime.date.today().strftime('%b-%d-%Y').lower()

def getDate(date_in_str):
  month = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
  _t = date_in_str.split('-')
  return datetime.date(int(_t[2]), month[_t[0]], int(_t[1]))

def getDigest(passwd):
  return hashlib.sha512(passwd+salt).hexdigest()

def isPasswd(passwd, digest):
  return getDigest(passwd) == digest

def tweak_phrase(ss):
  cc = eval(phrase)
  return ''.join(chr(ord(s)^ord(c)) for s,c in zip(ss, cc*1000))

def get_license_line(filename, pid):
  with open(filename, 'r') as f:
    for l in f.readlines():
      if l.startswith('PRODUCT_ID=%s '%pid):
        return l
  return None

def get_license_field(line, fid):
  field = line.split()
  for f in field:
    if f.startswith(fid):
      return f.split('=')[1]
  return None

def generate_license_file(today):
  embed = []
  sn = generate_sn(license_to+'-') 
  lfile = StringIO.StringIO()
  lfile.write(__license_header__+'\n\n')
  _server = __license_server__.format(mid=server)
  lfile.write(_server+'\n\n')
  embed.append(tweak_phrase(_server))

  for t in __products__:
    p = t[0]
    if not t[1]:
      continue
    val = today+p+tweak_phrase(sn)+expiration+server.lower()
    token = getDigest(val)
    _feature = __license_feature__.format(pid=p, sn=sn, expr=expiration, key=token)
    lfile.write(_feature+'\n\n')
    embed.append(tweak_phrase(_feature))

  with open(os.path.join(os.environ['DAVE_INST_DIR'],'dave.lic'),'w') as f:
    f.write(lfile.getvalue())
  return embed

today = printToday()
embeded_code = generate_license_file(today)

code = '''
import datetime
import hashlib
import os
import sys
import dave.mprobo.mchkmsg as mcode
from dave.mprobo.environ import EnvFileLoc

try:
  inst_dir = os.environ['DAVE_INST_DIR']
except:
  print "Check out the environment variable, 'DAVE_INST_DIR', is set correctly!"
  sys.exit()

tw = {tw}
twf = lambda ss: ''.join(chr(ord(s)^ord(c)) for s,c in zip(ss,tw*1000))
ecode = {ecode}
today = '{today}'
dlrpajfRkdy = twf('{salt}')

lfile = os.path.join(os.environ['DAVE_INST_DIR'],EnvFileLoc().def_lfname)

def getDe(date_in_str):
  month = {{'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}}
  _t = date_in_str.split('-')
  return datetime.date(int(_t[2]), month[_t[0]], int(_t[1]))

def getD(p):
  val = p+dlrpajfRkdy
  return hashlib.sha512(val).hexdigest()

def isP(p, d):
  return getD(p) == d

def getF(feature):
  d = []
  for l in open(lfile,'r').readlines():
    if l.startswith('PRODUCT_ID='):
      _f = l.split()
      if _f[0].split('=')[1]==feature:
        for __f in _f:
          ___f = __f.split('=')[1]
          d.append(___f)
        d.append(getDe(d[2]) >= datetime.date.today())
        return d
  return None
  
def get_midw():
  for l in open(lfile,'r').readlines():
    if l.startswith('SERVER='):
      return l.split('=')[1].strip()
  return None

def ehdnsxmgor(feature):
  d = getF(feature)
  val = today+d[0]+twf(d[1])+d[2]+get_midw().lower()
  if isP(val,d[3]) and d[4]:
    return True
  else:
    return  False

'''.format(ecode=embeded_code, today=today, salt=tweak_phrase(salt), tw=phrase)

with open(os.path.join(os.environ['DAVE_INST_DIR'],'dave/common/checkeval.py'),'w') as f:
  f.write(code)
