from numpy import *
from scipy import interpolate
from scipy.linalg import toeplitz,pinv,inv
from scipy.signal import invres,step,impulse
import matplotlib.pyplot as plt

class ModalAnalysis(object):
  ''' Fit an step response measurement to a linear system model '''
  def __init__(self, rho_threshold = 0.999, N_degree = 50):
    ''' set constraints on calculation '''
    self.rho_threshold = rho_threshold # correlation threshold
    self.N_degree = N_degree # Maximum degree of freedom

  def fit_stepresponse(self,h,t):
    ''' fit an step response measurement to a linear system model '''
    h_impulse = diff(h)/diff(t) # get impulse response from step response
    t_impulse = t[:-1]+diff(t)/2.0 # time adjustment, take the mid-point
    return self.fit_impulseresponse(h_impulse,t_impulse)
  
  def fit_impulseresponse(self,h,t):
    for N in range(2,self.N_degree):
      ls_result = self.leastsquare_complexexponential(h,t,N)
      rho = self.compare_impulseresponse(ls_result['h_impulse'],ls_result['h_estimated'])
      print('rho=',rho)
      if rho > self.rho_threshold:
        break
      if N == self.N_degree:
        print('[WARNING]: Maximum degree of freedom is reached when fitting response to transfer function')
    return ls_result

  def compare_impulseresponse(self,h1,h2):
    h1 = h1.flatten()
    h2 = h2.flatten()
    return corrcoef([h1,h2])[0,1]

  def leastsquare_complexexponential(self,h,t,N):
    ''' Model parameter estimation from impulse response
        using least-squares complex exponential method 
        h: impulse response measurement
        t: time range vector (in sec); must be uniformly-spaced
        N: degree of freedom
    '''
    no_sample = h.size
    if diff(t).max() > diff(t).max(): # check for uniform time steps
      spline_fn = interpolate.InterpolatedUnivariateSpline(t,h)
      t = linspace(t[0],t[-1],no_sample)
      h = spline_fn(t)
    h = h.reshape(no_sample,1)
    t = t.reshape(no_sample,1)
    M = no_sample - N  # no of equations
    dT = t[1]-t[0]
    # least-squares estimation of eigenvalues (modes)
    R = matrix(toeplitz(h[N-1::-1],h[N-1:no_sample-1]))
    A = -1*matrix(pinv(R.transpose()))*matrix(h[N+arange(0,M,dtype=int)])
    A0 = vstack((ones(A.shape[1]),A)).getA1()
    P = matrix(log(roots(A0)) / dT).transpose()
    # least-squares estimation of eigenvectors (modal coef)
    Q = exp(P * t.transpose())
    Z = pinv(matrix(Q.transpose()))*matrix(h)
    # return values
    num,den = invres(Z.getA1(),P.getA1(),zeros(size(P)),tol=1e-4,rtype='avg')
    print(num, den)
    num = num.real
    den = den.real
    h_estimated = Q.transpose()*Z
    h_estimated = h_estimated.real.getA1()
    return dict(h_impulse=h,h_estimated=h_estimated,num=num,den=den)

  def fit_transferfunction(self,H,f):
    ''' Fit a frequency response measurement to a linear system model '''
    pass

  def compare_transferfunction(self,H1,H2):
    ''' calculates the correlation coef. in frequency domain between two transfer function '''
    pass

  def selftest(self):
    pass

def main():
  X = ModalAnalysis(0.999,100)
  system = ([2.0],[1.0,2.0,1.0])
  #system = ([2.0,1.0],[1.0,2.0,1.0])
  ## impulse response test
  #t,h = impulse(system)
  #ls_result=X.fit_impulseresponse(h,t)
  #system_est = (ls_result['num'],ls_result['den'])
  #t1,h1 = impulse(system_est)
  #plt.plot(t,h,'rs',t1,h1,'bx')
  #plt.show()
  ## step response test
  t,h = step(system)
  ls_result=X.fit_stepresponse(h,t)
  system_est = (ls_result['num'],ls_result['den'])
  t1,h1 = step(system_est)
  plt.plot(t,h,'rs',t1,h1,'bx')
  plt.show()

if __name__ == "__main__":
  main()
