
import datetime
import hashlib
salt = 'Ehdnsxmgor1!'
eday = 32
token=['c1ab7a4fa276916b44f8b5bafe9ed184024d6cfe06ece2254bdf02d485fdf11d', '21d092979ffb17a54069cc0632c81f6077ad0e6de1a11feb6301c921e366b483', 'af8c5fb4b041a7c90c22b3e96296f9ac4fe82ab115f87fc28cae7caabc3bc6e0', '198509a53ccb29f911289db0544286ac90acb3237b79c306cf0353b35892c3ed', '776c76d5543723f7b2c1381e222752faaf95e07d7929a807bbed668e64120ec4', '367c2a9bfe8217f8a4a72747aceec96827f4010c87f3c40540a767d33d518d4b', '1f24c8abc9aa552aac0cdfefc37ef2b3e483b42f5a10fcb04cfa40b938e7bcfd', '226efc3c7ea3f25221cc3f9a013b8444311d213e2041860523c893963ae8c05c', 'a0d9bd1e09571e77bca1e08c70854e3990b02f3fe807554925806103dbb45bc3', 'be18615985ccf3f32290691845cde927164bdab6f9c42db851724857e8bbb02b', '84e6efcb58c6d7d4b8dbb6986346e292aac8e0fa4b5f870390fb5ad53325e7c6', 'bcac5289662b58925f0da73768021c9ee75c606e7ae69666b7612266188414e5', '0d74196da89a605a4de1d5f211da3ba273ab4b03060bd0f8d61434ac0acbb408', '234b48f82ccf56966eda7e830dff37bcaff2fa96d4144d701983fd194e51b4b9', '96b90fa0f81f23758f77309a878a77fc09459e7695b70cf6c918437c72218cbb', '2bd69b899876384de2a8065db1f094f4f034657b8d9c9dfd84c3d0896f62fbb4', 'b8dfe1d99665a72202cb44995b250572a68df2669b01bb928c3a76db382897e0', '99de3cf5524a5309358ce441835b1dad4d2647c5df383ad2780cb687bc31d30c', '32a4854327bdd5884a2594ed370cda37af1c88d9fa49cb4bafc3e8767bb5ba04', '2fed86e41aabd3bd2b90e64a33043c989e627948864bbe979678c3c6af7e2f75', 'c06b31297ad36da6a85fa661e399e627ac27f7ef9d6d8267fbf1c21578d8d0ce', 'cc4132b055f7a5a519491d582c59c2ba2ecec4753c135fcd628c236808b7bd7d', '82497419c2a1af8802469234e8bf921c321fbd32ed0cf68f35ad3132d2845656', '8f65fe626f387f3f28caa353dfd5148fb544abec2f0a70fe15f1a091a43fc53b', 'e9add335c9e2d494550ab80b4359be8b1ae3134afe3b857a7801b7814894aada', '36f632ee9ef4d7a368e26856617d0003f20d8c3f9a1432f555ee58bc4c12f55c', '1c8c8f8a3d32774835c066045f4409867ba3829c3d0f836859665207c4f89cb8', '4ab5ab45aab1a876adef034e6339f2019fea7fb7c65f3895553e1d444542128e', '159b46a65201219c76ef27cdf324fe40ceeaaa25e85fcfc05739f44645026507', 'c49d525f5dd2002310f373f7fa08d59654425fa5335333ced9a83993f6fb0909', '3e48bd4db2d460d8dbb6952be53e8e25a8fc6b050bbf992b1dace6e310bccf4d']
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

