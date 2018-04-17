****************************
Look-Up Table Based Modeling
****************************

While non-uniformly sampled PWL modeling boost the simulation speed, there still seems to be room for improvement. 


Background
==========

Let's first think about a single-pole model like this.

.. math::
  f(t) = \alpha_i\cdot e^{t/\beta_i}
  :label: eq_aexp

One of the difficulties to use lookup table here is that :math:`\alpha_i` may not be a static value; it could change during simulation. In detail, to meet a certain error tolerance, :math:`e_{tol}`, the PWL modeling of the exponential term (:math:`e^x`) should have the error tolerance of :math:`e_{tol}/\alpha_i` and this error tolerance is still varying, such that it is not simple to make a lookup table for the exponential term.

However, let's step back a little bit and for PWL approximation, use relative error instead of absolute error. Let's say the PWL equation for Equation :eq:`eq_aexp` is given by

.. math::
  \hat{f}(t) = \alpha_i\cdot (a\cdot t + b).
  :label: eq_pwl

Then, the relative of error of this approximation is as follows.

.. math::
  \mathrm{relative}\;\mathrm{error} & = \frac{|f(t)-\hat{f}(t)|}{f(t)}
                          & = \frac{|e^{t/\beta_i}-(a\cdot t + b)|}{e^{t/\beta_i}}
  :label: eq_relerr                       

After changing the variable :math:`t` (i.e. normalize to :math:`\beta_i`) to :math:`x`, the relative error is given by

.. math::
  \mathrm{relative}\;\mathrm{error} = \frac{|e^{x}-(a\cdot \beta_i\cdot t + b)|}{e^{x}}
  :label: eq_normalize 

where :math:`x=t/\beta_i`. Therefore, we could approximate the normalized exponential function (:math:`e^x`) to a PWL function with a certain relative error, which allows to build a lookup table of paired vector (:math:`x_i`, :math:`e^{x_i}`). From the LUT, we could retrieve series of time sequences to create events and the corresponding values without any calculation/DPI function calls during Verilog simulation.

The other benefit of using this LUT is that you can create a optimal number of events. While the previous algorithm (with absolute error constraints) is conservative, one could find the optimal one since there is no simulation cost to build such a LUT before Verilog simulation.

