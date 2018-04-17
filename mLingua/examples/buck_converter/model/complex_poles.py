# Since p1 & p2 of TF are a complex numbers, and the filter generator doesn't support complex poles, zeros yet, this routine helps to get the expression 

from sympy import *
si, CL, L, yo0, yo1, t = symbols('si CL L yo0 yo1 t', real=True)
poler, polei = symbols('poler polei', real=True)
p1, p2 = symbols('p1 p2', complex=True)
p1 = poler + I*polei
p2 = poler - I*polei

#y = (CL*L*p1*p2*yo0 + CL*L*p2*yo1 - si)*exp(-p2*t)/(CL*L*p2*(p1 - p2)) - (CL*L*p1*p2*yo0 + CL*L*p1*yo1 - si)*exp(-p1*t)/(CL*L*p1*(p1 - p2)) + si/(CL*L*p1*p2)

y1 = si/(CL*L*p1*p2)
y1 = re(y1.expand())
y2 = re((CL*L*p1*p2*yo0 + CL*L*p2*yo1 - si)/(CL*L*p2*(p1 - p2))*exp(-poler*t)*(cos(polei*t)+I*sin(polei*t)))
y3 = re(-1*(CL*L*p1*p2*yo0 + CL*L*p1*yo1 - si)/(CL*L*p1*(p1 - p2))*exp(-poler*t)*(cos(-polei*t)+I*sin(-polei*t)))

y = y1 + y2 + y3

# real part of y(t)
yr = y
# second derivative of yr
y2r = diff(y, t, 2)

#pprint(yr)
#pprint(y2r)
print '='*10, 'y(t)', '='*10
print yr
print ''
print '='*10, 'y"(t)', '='*10
print re(y2r)
