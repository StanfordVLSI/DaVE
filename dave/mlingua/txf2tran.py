#!/usr/bin/env python
# Take LTI system transfer function in terms of poles and zeros
# Show the corresponding symbolic expression in time domain

from sympy import Symbol, symbols, Poly, pprint, inverse_laplace_transform, S, collect, exp, apart_list, assemble_partfrac_list, Wild, Function
from sympy.polys.partfrac import apart

"""
Configuration example

# Take LTI system transfer function in terms of poles and zeros
# Show the corresponding symbolic expression in time domain

# configuration file example for tf2tr.py

from sympy import Symbol, exp

# 't' and 's' are variables in time and s-domain, respectively.

#------------------------------------------
# STARTS: do not touch the belows statement
#------------------------------------------
symbol = symbol + ' ' + 't s si si_a si_b'
for v in symbol.split(): vars()[v] = Symbol(v, real=True)
#------------------------------------------
# ENDS: do not touch the belows statement
#------------------------------------------

###################################################################################
# Define a tuple of factors if you want your expression to be factored by the terms
# Leave this () if you don't want to do so.
###################################################################################
factor = (exp(-p1*t),)

###############################
# Define Transfer function (TF)
# TF = numerator/denumerator
###############################
numerator= s
denumerator= (s+p1)
"""

class Txf2Tran(object):
  ''' s-domain to time domain response conversion tool
  '''
  def __init__(self, numerator, denumerator, input_type):
    '''
      numerator, denumerator: num/denum of a transfer function in string format
      input_type: 'real' for piecewise constant input, 'pwl' for piecewise linear input
    '''
    self.__yt = self._run(numerator, denumerator, input_type)

  def get_yt(self):
    return self.__yt

  def __print_fn(self, s, f):
    print '='*len(s)
    print s
    print '='*len(s)
    print ''
    pprint(f)
    print '\n'
  
  def __get_order(self, expr):
    s = Symbol('s', real=True)
    ais = Poly(expr, s).all_coeffs()
    order = len(ais) - 1
    return ais, order
  
  def __get_init_expr(self, ais, n, prefix):
    ''' generate equation in string for non-zero state response '''
    expr = []
    for i, a in enumerate(ais):
      _tmp = []
      for j in range(0, n-i):
        s_order = n-i-j-1
        if s_order > 1:
          s = 's**%d*%s%d' % (s_order, prefix, j)
        elif s_order == 1:
          s = 's*%s%d' %(prefix, j)
        else:
          s= '%s%d' % (prefix, j)
        _tmp.append(s)
      if _tmp != []:
        expr.append( '(%s)*(%s)' %(a, '+'.join(_tmp)))
    return '+'.join(expr)
  
  def __convert_to_basis_expr(self, mdict):
    ''' return an expression into a format recognized by vlog filter generator '''
    _K = Wild("_K")
    _p = Wild("_p")
    _m = Wild("_m") 
    if mdict[_p] == 0:  # no exp
      if mdict[_m] == 1:
        return ('const', str(mdict[_K]))
      elif mdict[_m] == 2:
        return ('t', str(mdict[_K]))
      elif mdict[_m] == 3:
        return ('t**2', str(mdict[_K]))
    else:
      if mdict[_m] == 1:
        return ('exp', str(mdict[_K]), str(1/mdict[_p]))
      elif mdict[_m] == 2:
        return ('t*exp', str(mdict[_K]), str(1/mdict[-p]))
  
  def __inv_laplace(self, tf_terms):
    ''' custom inverse laplace '''
    _K = Wild("_K")
    _p = Wild("_p")
    _m = Wild("_m") 
    t = Symbol('t',real=True)
    s=Symbol('s', real=True) # Why does 's' symbol disappear
    y = 0
    basis_expr = []
    for e in tf_terms:
      fixproblem = False
      mdict = e.match(_K/(s+_p)**_m)
      for v in mdict.values(): # need this because of sympy.match bug
        if list(v.find(s)) != []:
          fixproblem = True
      if fixproblem:
        mdict = e.match(_K/s)
        mdict[_p] = 0
        mdict[_m] = 1
      term = mdict[_K]*t**(mdict[_m]-1)*exp(-mdict[_p]*t)
      basis_expr.append(self.__convert_to_basis_expr(mdict))
      y += term
    return y, basis_expr
  
  
  ###########################################################
  # Implementation starts here
  ###########################################################
  
  def _run(self, num_str, denum_str, in_type):
    in_allowed = ['real', 'pwl']
    assert in_type in in_allowed, 'Allowed input stimulus should be among %s' % in_allowed
    
    # create symbols
    rsvd_var = ['t', 's', 'si', 'si_a', 'si_b']
    expr = S('('+num_str+')/('+denum_str+')')
    for x in expr.atoms():
      if str(x) not in rsvd_var:
        try:
          float(x)
        except:
          vars()[str(x)] = Symbol(str(x), real=True)

    t, s, si, si_a, si_b = symbols(' '.join(rsvd_var), real=True)
    
    # transfer function
    num = eval(num_str)
    denum = eval(denum_str)
    TF = num/denum
    
    # input
    if in_type == 'pwl':
      xin = si_a/s + si_b/s**2
      in_str = 'ramp'
    else:
      xin = si/s
      in_str = 'step'
    
    # forced response
    Ysf = (TF*xin) # forced respose
    
    # natural response
    ais_d, order_denum = self.__get_order(denum)
    ais_n, order_num = self.__get_order(num)
    
    yos = ['yo%d' % x for x in range(order_denum)] 
    for v in yos:
      vars()[v] = Symbol(v, real=True)
    xis = ['xi%d' % x for x in range(order_denum)] 
    for v in xis:
      vars()[v] = Symbol(v, real=True)
    
    s=Symbol('s', real=True) # Why does 's' symbol disappear
    init_yo = self.__get_init_expr(ais_d, order_denum, 'yo')
    init_xi = self.__get_init_expr(ais_n, order_num, 'xi')
    init_expr = init_yo
    if init_xi != '': 
      init_expr = init_expr + '-' + init_xi
    Ysn = eval(init_expr)/denum # I hate eval(), but S() and parse_expr() screw me
    
    Ys = Ysf + Ysn # Complete Transfer function
    Ys_pfd = apart(Ys, s)
    yt, yt_basis = self.__inv_laplace(Ys_pfd.as_ordered_terms()) # complete time-domain response
    
    # sort out basis
    yt_basis.sort(key=lambda tup:tup[0])
    
    self.__print_fn('Transfer Function', TF)
    self.__print_fn('Forced response in s-domain to %s input' % in_str, Ysf)
    self.__print_fn('natural response in s-domain', Ysn)
    self.__print_fn('Complete response in s-domain after partial fraction decomposition', Ys_pfd)
    self.__print_fn('Complete response in time domain to %s input' % in_str, yt)
    
    print '='*40
    print 'Nonpretty expression for y(t)' 
    print '='*40
    print 'y(t)= ', yt
    
    return yt_basis
