# Symbol equation analysis

import re
import sympy as sym

class WaveFunction(object):
  ''' This takes a mathmatical expression (sympy format),
      and spit out Verilog expeession of first/second derivative 
      of the expression as well as the expression itself.

  >>> f='a*(1.0 - exp(-t/tau)) + b*t + b*tau*(-1.0 + exp(-t/tau)) + v0*exp(-t/tau)'
  >>> wf = WaveFunction(['log'])
  >>> wf.load_expression(f, 't')
  >>> wf.get_user_fn()
  ('a*(1.0 - exp(-t/tau)) + b*t + b*tau*(-1.0 + exp(-t/tau)) + v0*exp(-t/tau)', 'a*exp(-t/tau)/tau + b - b*exp(-t/tau) - v0*exp(-t/tau)/tau', '(-a/tau + b + v0/tau)*exp(-t/tau)/tau')
  >>> wf.get_var()
  ['a', 'tau', 'b', 'v0', 't']
  >>> wf.get_math_fn()
  ['exp']
  >>> wf.xxx()
  '''
  def __init__(self, rsvd_word=[]):
    ''' 
      rsvd_word: reserved word like basic functions
    '''
    self.__rsvd_word = ['exp', 'sin', 'cos'] + rsvd_word
    self.__ivar = 't'

  def load_expression(self, expr, ivar):
    __sym = set(re.findall(r'[a-zA-Z_]\w*', expr))
    self.__var = list(__sym-set(self.__rsvd_word))
    self.__call = list(set(__sym)-set(self.__var))
    self.__expr_fn = expr
    self.__load_symbol()
    self.__set_ivar(ivar)

  def get_user_fn(self):
    return self.__expr_fn, self.__expr_fn1, self.__expr_fn2
  
  def get_var(self):
    return self.__var

  def get_math_fn(self):
    ''' return the basic functions called '''
    return self.__call

  def __set_ivar(self, ivar):
    ''' set independent variable '''
    assert ivar in self.__var, "Independent variable %s doesn't exist" % ivar
    self.__ivar = ivar

  def __load_symbol(self):
    for v in self.__var:
      vars()[v] = sym.Symbol(v)
    self.__symexpr = sym.expand(sym.sympify(self.__expr_fn))
    f1 = self.__get_derivative(self.__ivar, 1)
    f2 = self.__get_derivative(self.__ivar, 2)
    self.__expr_fn1 = str(f1)
    self.__expr_fn2 = str(f2)
    self.__expr_fn  = str(self.__symexpr)

  def __get_derivative(self, var, order):
    return sym.expand(sym.diff(self.__symexpr, var, order))

  def xxx(self):
    print re.search(r'\((w+)\)', self.__expr_fn).group(1)

def main():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  main()
