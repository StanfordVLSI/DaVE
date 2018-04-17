# Test out PWL waveform generator

import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

class PWLSignal(object):
  ''' a signal consists of 
      initial value and its slope over time 

  >>> sig = PWLSignal(0.1, 1.0)
  >>> print sig.v0()
  0.1
  >>> print sig.slope()
  1.0
  '''
  def __init__(self, v0=0.0, slope=0.0):
    self.__v0 = v0  # initial value
    self.__slope = slope  # signal slope

  def v0(self):
    ''' return initial value '''
    return self.__v0

  def slope(self):
    ''' return slope value '''
    return self.__slope

class PWLVector(object):
  ''' Time series where
        - x: list of time
        - y: list of PWLSignal instance
      We assume that the PWL signal is continuous: see how self.add() function works 
        - You first set the initial value of the PWLVector by set_v0()

  >>> pwlsig = PWLVector()
  >>> pwlsig.set_init(0.0, 0.1)
  >>> pwlsig.add(0.3, 1.9)
  >>> pwlsig.add(0.5, 8.3)
  >>> x = np.linspace(-0.1, 1.0, 40)
  >>> y = pwlsig.predict(x)
  >>> fig = pwlsig.plot(x, 'time', 'signal', 'PWL waveform', filename='wv_pwlgenerator.png')
  >>> pwlsig.get_inflection_pts()
  [(0.0, 0.3, 0.5), (0.1, 1.9, 8.3)]

  '''
  def __init__(self, x=[], y=[]):
    self.__data = zip(x, y)
    assert len(x) == len(y), 'Vector size mismatch'

  def set_init(self, x, y):
    ''' set the initial value of this Vector '''
    self.__x0 = x
    self.__y0 = y

  def add(self, x, y):
    ''' add a signal to self.__data
    '''
    self.__data.append((self.__x0, PWLSignal(self.__y0, self.get_slope(x, y))))
    self.__x0 = x
    self.__y0 = y

  def get_slope(self, x, y):
    return (y-self.__y0)/(x-self.__x0)

  def plot(self, x, xlabel, ylabel, title, y=None, filename=None, fig=None, legend=None, annotate=True):
    ''' plot the waveform for given list of x 
      if y is None: plot the predicted value of x
    '''
    fignum = fig.number if fig is not None else None
    fig = plt.figure(fignum)

    options=dict(label = legend) if legend else {}

    xs = self.x()
    xs, ys = self.get_inflection_pts()
    plt.scatter(xs, ys, c='r', marker='o', s=40) # plot inflection points
    if annotate:
      antext = ['(%s,%s)' %(to_engr(xs[i]), to_engr(ys[i])) for i in range(len(ys))]
      map(lambda x: plt.text(*x), zip(xs, ys, antext)) # annotate inflection points
    if y==None:
      plt.plot(x, self.predict(x), **options) # plot predicted points 
    else:
      plt.plot(x, y, **options) # plot predicted points 
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    v = plt.axis()
    plt.axis([min(x), max(x), v[2], v[3]])

    if legend: plt.legend()
    if filename is not None: plt.savefig(filename)

    return fig
    
  def predict(self, x=[]):
    ''' predict the values for given series of x '''
    return map(self.at, list(x))

  def __print_vector(self):
    print self.get_series()

  def get_series(self):
    return [(x, v.v0(), v.slope()) for x, v in self.__data]

  def get_inflection_pts(self):
    ''' return inflection points of the Vector '''
    return zip(*[(x, v.v0()) for x, v in self.__data] + [(self.__x0, self.__y0)])

  def len(self):
    ''' return the length of this Vector '''
    return len(self.__data)

  def at(self, x):
    ''' find a value at x '''
    x0, y = self.xy_at_x(x)
    return y.v0() + y.slope()*(x-x0)

  def xy(self):
    ''' return x & y '''
    return zip(*self.__data)

  def x(self):
    ''' return x only '''
    return list(self.xy()[0])

  def y(self):
    ''' return y only '''
    return list(self.xy()[1])

  def xy_at_x(self, x):
    ''' return x & y pair valid for given x value '''
    idx = [i for i, v in enumerate(self.x()) if x >= v]
    idx = 0 if idx==[] else idx[-1] # fix if out of range
    return self.x()[idx], self.y()[idx]

def main():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  main()
