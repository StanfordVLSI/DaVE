# PWL Basis function expression

import re
import sympy as sym

class PWLBasisFunctionExpr(object):
  ''' This generates two function expressions as string
    - expr: a sum of basis functions to represent a response signal
    - expr_1: an expression derived from "expr" to calculate the time interval of PWL approximate waveform
  >>> bf = PWLBasisFunction()
  >>> bf.get([('exp',1.2,0.5), ('t*exp',0.8,1.2), ('exp*cos', 0.9, 1.5, 6.0) ])
  '''

  def __init__(self, term=[]):
    self.basis = {'const': self.__get_const, # if the term is a constant
                  't' : self.__get_t,
                  't**2' : self.__get_t2,
                  'exp' : self.__get_exp, 
                  't*exp' : self.__get_texp, 
                  'exp*cos' : self.__get_expcos,
                  'exp*sin' : self.__get_expsin,
                  'cos' : self.__get_cos,
                  'sin' : self.__get_sin,
                  'sqrt': self.__get_sqrt
                 }
    self.__build(term)

  def __build(self, term=[]):
    ''' get the expression as a string
    '''
    for t in term:
      if t[0] not in self.basis:
        return '', ''
    t = zip(*[self.basis[t[0]](t[1:]) for t in term])
    def filter_None(inlist):
      return filter(lambda x: x != None, inlist)
    expr = ' + '.join(filter_None(t[0]))
    expr_1 = ' + '.join(filter_None(t[1]))
    self.__expr, self.__expr_fn = self.__process_expr(expr)
    self.__expr_1, self.__expr_1_fn = self.__process_expr(expr_1)
    print ''
    print 'Expression for PWL approximation = ', self.__expr
    print 'Expression for calculating time interval = ', self.__expr_1
            
  def get_fn_str(self):
    return self.__expr, self.__expr_1

  def get_fn(self):
    return self.__expr_fn, self.__expr_1_fn

  def get_derivative_str(self, order):
    lbf = LambdifyPWLBasisFunctionExpr()
    lbf.load_expression(self.__expr, 't')
    return lbf.get_derivative_str(order)

  def __process_expr(self, expr):
    lbf = LambdifyPWLBasisFunctionExpr()
    lbf.load_expression(expr, 't')
    return lbf.get_fn_str(), lbf.get_fn()
    
  def __get_const(self, term):
    expr = '{0}'.format(term[0])
    expr_1 = None
    return expr, expr_1

  def __get_t(self, term):
    expr = '({0})*t'.format(term[0])
    expr_1 = None
    return expr, expr_1

  def __get_t2(self, term):
    expr = '({0})*t**2'.format(term[0])
    expr_1 = '2.0*abs({0})'.format(term[0])
    return expr, expr_1

  def __get_exp(self, term):
    expr = '({0})*exp(-1.0*t/({1}))'.format(term[0], term[1])
    expr_1 = 'abs({0})/({1})**2*exp(-1.0*t/({1}))'.format(term[0], term[1])
    return expr, expr_1

  def __get_texp(self, term):
    expr = '({0})*t*exp(-1.0*t/({1}))'.format(term[0], term[1])
    expr_1 = 'abs(({0})*(-2.0+t/({1}))/({1}))*exp(-1.0*t/({1}))'.format(term[0], term[1])
    return expr, expr_1
  
  def __get_expcos(self, term):
    expr = '({0})*exp(-1.0*t/({1}))*cos(({2})*t)'.format(term[0], term[1], term[2])
    expr_1 = 'abs(({0})*(({2})**2 + 2.0*({2})/({1}) + 1.0/({1})**2))*exp(-1.0*t/({1}))'.format(term[0], term[1], term[2])
    return expr, expr_1

  def __get_expsin(self, term):
    expr = '({0})*exp(-1.0*t/({1}))*sin(({2})*t)'.format(term[0], term[1], term[2])
    expr_1 = 'abs(({0})*(({2})**2 + 2.0*({2})/({1}) + 1.0/({1})**2))*exp(-1.0*t/({1}))'.format(term[0], term[1], term[2])
    return expr, expr_1

  def __get_cos(self, term):
    expr = '({0})*cos(({1})*t+{2})'.format(term[0], term[1], term[2])
    expr_1 = 'abs(-1.0*({0}))*({1})**2'.format(term[0], term[1])
    return expr, expr_1

  def __get_sin(self, term):
    expr = '({0})*sin(({1})*t+{2})'.format(term[0], term[1], term[2])
    expr_1 = 'abs(1.0*({0}))*({1})**2'.format(term[0], term[1])
    return expr, expr_1

  def __get_sqrt(self, term):
    expr = 'sqrt(t)'
    expr_1 = 'sqrt(t)'
    return expr, expr_1

class LambdifyPWLBasisFunctionExpr(object):
  '''
    Lambdify PWL basis function expression for verifying PWL approximating algorithm
  '''
  def __init__(self, rsvd_word=[]):
    ''' 
      rsvd_word: reserved word like basic functions
    '''
    self.__rsvd_word = ['exp', 'sin', 'cos', 'sqrt'] + rsvd_word
    self.__ivar = 't'

  def get_fn(self):
    ''' return lambda function '''
    return sym.lambdify(self.__ivar, self.__symexpr)

  def get_fn_str(self):
    ''' return the expression as a string '''
    return self.__expr_fn

  def get_derivative_str(self, order):
    return sym.simplify(sym.diff(self.__symexpr, self.__ivar, order))

  def load_expression(self, expr, ivar):
    __sym = set(re.findall(r'[a-zA-Z_]\w*', expr))
    self.__var = list(__sym-set(self.__rsvd_word))
    self.__call = list(set(__sym)-set(self.__var))
    self.__expr_fn = expr
    self.__load_symbol()
    self.__set_ivar(ivar)

  def __set_ivar(self, ivar):
    ''' set independent variable '''
    #assert ivar in self.__var, "Independent variable %s doesn't exist" % ivar
    self.__ivar = ivar

  def __load_symbol(self):
    for v in self.__var:
      vars()[v] = sym.Symbol(v)
    self.__symexpr = sym.expand(sym.sympify(self.__expr_fn))

def main():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  main()
