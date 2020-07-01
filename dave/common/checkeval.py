
import datetime
import hashlib
import os
import sys
import dave.mprobo.mchkmsg as mcode
from dave.mprobo.environ import EnvFileLoc

try:
  inst_dir = os.environ['DAVE_INST_DIR']
except:
  print("Check out the environment variable, 'DAVE_INST_DIR', is set correctly!")
  sys.exit()

tw = mcode.INFO_020
twf = lambda ss: ''.join(chr(ord(s)^ord(c)) for s,c in zip(ss,tw*1000))
ecode = ['\x12\x08\x01v(=Y\t\x03C\x04\x1d\x1d\x06\x05\x15']
today = 'jan-22-2019'
dlrpajfRkdy = twf('%7N	RTP')

lfile = os.path.join(os.environ['DAVE_INST_DIR'],EnvFileLoc().def_lfname)

def getDe(date_in_str):
  month = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
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
  return True
  #d = getF(feature)
  #val = today+d[0]+twf(d[1])+d[2]+get_midw().lower()
  #if isP(val,d[3]) and d[4]:
  #  return True
  #else:
  #  return  False

