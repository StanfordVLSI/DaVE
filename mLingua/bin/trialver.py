# make a trial version s/w

import datetime
import hashlib
import random

salt = 'Ehdnsxmgor1!'
def getDigest(passwd):
  return hashlib.sha256(passwd+salt).hexdigest()

def isPasswd(passwd, digest):
  return getDigest(passwd) == digest

refdate = datetime.date.today() 
delta = 31 # days of evaulation

token = []

for i in range(delta):
  d = refdate + datetime.timedelta(i)
  val = str(d.year) + str(d.month) + str(d.day)
  token.append(getDigest(val))

random.shuffle(token)
#data = token[0:len(token)/2] + [salt] + token[len(token)/2:]
data = token

code = '''
import datetime
import hashlib
salt = '{salt}'
eday = {eval_days}
{data}
def getDigest(passwd):
  #return hashlib.sha256(passwd+token[(len(token)-1)/2]).hexdigest()
  return hashlib.sha256(passwd+salt).hexdigest()

def isPasswd(passwd, digest):
  return getDigest(passwd) == digest

def ehdnsxmgor():
  d = datetime.date.today()
  val = str(d.year) + str(d.month) + str(d.day)
  if getDigest(val) in token:
    return True
  
def ghktdjvn():
  i = get_maxd()
  if i < 0:
    return 'It is already expired !!!'
  else:
    expr_date = datetime.date.today() + datetime.timedelta(i)
  return 'Expiration date: %s' % (expr_date.strftime("%Y-%m-%d"))

def get_maxd():
  for i in range(eday):
    d = datetime.date.today() + datetime.timedelta(i)
    val = str(d.year) + str(d.month) + str(d.day)
    if getDigest(val) not in token:
      return i-1

'''.format(data = 'token=%s'%data, eval_days = delta+1, salt=salt)

with open('../pwlgen/checkeval.py','w') as f:
  f.write(code)
