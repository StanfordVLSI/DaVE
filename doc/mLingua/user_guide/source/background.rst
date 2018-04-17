**********
Background
**********
This section describes the theoretical background of this work.

Abstract
========
As analog and digital systems are strongly coupled, there is strong need for high-level functional models of analog circuits to validate the whole mixed-signal systems.  The challenge is to create fast models without loosing accuracy. 

Introduction
============

Piecewise Linear Analog Model
=============================
As shown in Figure :ref:`analogmodel`, our analog model essentially consists of two parts; a DC transfer curve model and a filter model. The former part describes the static behavior of a circuit using a linear model, but is not necessarily a perfect line. We use ``piecewise`` linear model so that nonlinear characteristics (e.g. compressed gain) are captured in the model. The latter part depicts the dynamic behavior of a circuit using a linear filter model. With some user inputs, we provide utilities to generate these two parts automatically.

.. _analogmodel:

.. figure:: _static/analog_model.png
  :width: 400px
  :align: center

  Block digram of an analog model.

Static Transfer Curve Model
---------------------------
In piecewise linear (PWL) waveform approximation, the PWL representation of a static transfer curve is a bit complicated than in piecewise constant waveform. Since a PWL signal conveys its slope as well as its offset value, the signal could cross over the boundary of the PWL transfer curve (where the transfer gain is different) in the future, even if the signal will not change. Therefore, the model should be able to predict when the signal could cross the boundaries of the transfer curve and create events to handle the inflection of the transfer curve.

.. figure:: _static/txfcurve_event.png
  :width: 400px
  :align: center

  Creation of events for handling PWL static transfer curve.

Our implementation of a static curve model is briefly described in the model below. [#]_ Let's assume that the PWL transfer curve is given as a lookup table; the output (``ly``) vs the input (``lx``), and the gain (``lgain``) vs the input (``lx``). An event is created when either input (``in``) changes or self-triggered event (``wakeup``) occurred. Then, it retrieves the region in which the current input value is located from ``lx``, calculates the output by scaling the input with the gain (``lgain``) value. The next step is to project when the input PWL signal will cross the inflection point of the transfer curve. From the sign of the PWL signal's slope, one could know the inflection point of the transfer curve that the signal is heading to and thus the arrival time of the point. A new event (``wakeup``) after ``dT`` is then scheduled.

.. literalinclude:: _static/txf_procedure.v
  :linenos:
  :language: verilog

Since this transfer curve model should have a very regular format, we create a utility (``dctxf.py``) in python that takes a configuration file and generates a transfer curve model in SystemVerilog to a PWL signal. The required user inputs are a few as shown below.

+--------------+--------------------------------------------------------------------+
| Parameter    | Description                                                        |
+==============+====================================================================+
| module_name  | Generated Verilog module (and file) name                           |
+--------------+--------------------------------------------------------------------+
| x            | array of x data representing a static curve                        |
+--------------+--------------------------------------------------------------------+
| y            | array of y data representing a static curve                        |
+--------------+--------------------------------------------------------------------+
| use_userdata | | Reduce user data to meet the error tolerance (``etol``) if False |
|              | | Use the original x, y data for the model creation if True        |
+--------------+--------------------------------------------------------------------+
| etol         | error tolerance if data reduction is performed                     |
+--------------+--------------------------------------------------------------------+

The below code is an example of the configuration file. The data points (``x``, ``y``) could be from either simulation data or some sampled data points of an analytic equation. Running the utility (``dctxf.py``) with this input will produce a SystemVerilog model as well as two data plots which show the data reduction of the original data and the error due to the data reduction.

.. literalinclude:: _static/cfg_txf2.py
  :language: python


.. literalinclude:: _static/limiter2.v
  :language: verilog

.. _limiter2data:


.. figure:: _static/limiter2_data.png
  :width: 400px
  :align: center

  A static transfer curve of ``limiter2.v``.


.. figure:: _static/limiter2_err.png
  :width: 400px
  :align: center

  Approximation errors in :ref:`limiter2data`.

Analog Filter Model
-------------------
We represents the dynamic behavior of an analog circuit as a ramp response of an linear system. For given transfer function of a system in s-domain, we create an equivalent time-domain model to a ramp input (i.e. a PWL signal input) in event-driven SystemVerilog. [#]_

The pseudo code below describes how the filter model works. When an input changes at :math:`t=t_{cur}`, it will create a time-stamp (``t0``) which serves as a time reference of the response function. The output response and the input at the moment will also be stored as an initial condition (``out0``) and a forced input (``si_at_t0``) of a new response, respectively. When input does not change, the event of a self-triggered signal (``wakeup``) is scheduled to approximate the real-time response to a PWL waveform. It predicts the next evaluation time (:math:`t_{cur}+dT`) should be, the output value at that time with the algorithm described in :ref:`timestepcontrol`. Then, it schedule an event at :math:`t_{cur}+dT` with ``wakeup`` signal. The details of calculating ``dT`` is explained in :ref:`timestepcontrol`.

.. literalinclude:: _static/filter_event.v
  :language: verilog
  :linenos:

Alike the transfer curve model, this filter model can be automatically generated by a script (``filtergen.py``) with some user inputs. A configuration file, its generated Verilog model, and AC simulation result of a single pole filter is shown below.


.. literalinclude:: _static/cfg_filter.py
  :language: python

.. literalinclude:: _static/filter_p1.v
  :language: verilog

.. figure:: _static/ac_sim_filter_p1.png
  :width: 400px
  :align: center

  Frequency response of the generated single-pole filter model (pole frequency=20 MHz).

.. _timestepcontrol:

Time-Step Control
=================
This section describes the algorithm to calculate non-uniform time interval of PieceWiseLinear (PWL) waveform approximation for modeling the transient response of an analog filter.

Background
----------
Some literature showed that the upper bound of the PWL approximation error, :math:`|e_{tol}|` is given by 

.. math::
  |e_{tol}| \leq \frac{1}{8}\cdot \Delta t^2 \cdot \max_{t_0 \leq t \leq t_0+\Delta t} |f''(t)|
  :label: eq_etol

where :math:`\Delta t` is the next time interval at :math:`t=t_0`, and :math:`f''(t)` is the second derivative of the waveform function :math:`f(t)`.

After rearranging of Equation :eq:`eq_etol`, one could get the time interval as follows.

.. math::
  \Delta t = \sqrt{\frac{8\cdot |e_{tol}|}{\max_{t_0 \leq t \leq t_0+\Delta t} |f''(t)|}}
  :label: eq_deltat

Calculating :math:`\Delta t` in Equation :eq:`eq_deltat` requires some iteration since :math:`\max |f''(t)|` for the interval :math:`t_0 \leq t \leq t_0+\Delta t` is not a closed-form equation, resulting in slow simulation speed.

.. _algorithm:

Non-Iterative Algorithm
-----------------------
To calculate the time interval :math:`\Delta t` without any iteration, we leverage the fact that the type of basis functions for analog filter response is quite limited, since the filter is usually modeled as a linear system. In general, the transient response of a linear system can be represented as a sum of complex exponential functions as follows.

.. math::
  f(t) = \sum_{i=0}^N \alpha_i \cdot e^{\beta_i\cdot t}
  :label: eq_analog_response

where :math:`\alpha_i \cdot e^{\beta_i\cdot t}` is a scaled complex exponential function. Since we need time-domain response, we want :math:`\alpha_i` and :math:`\beta_i` to be real numbers: oscillatory behavior is handled later. In addition, :math:`\beta_i` should be a non-positive real numbers for bounded output.

Let us start with a single decaying exponential function like this.

.. math::
  f(t) = \alpha_i \cdot e^{\beta_i\cdot t}, \quad \alpha_i \in \mathbb{R} \; \mathrm{ and }\; \beta_i \in \mathbb{R^-}
  :label: eq_decaying_fn
  
Then, the second derivative of this :math:`f(t)` is a scaled version of :math:`f(t)`. In other words, the absolute value of the second derivative is also a decaying function, resulting in a closed-form equation for calculating :math:`\Delta t` as follows.

.. math::
  f''(t) = \alpha_i \cdot \beta_i^2\cdot e^{\beta_i\cdot t},
  :label: eq_f2t

.. math::
  \max_{t_0 \leq t \leq t_0+\Delta t} |f''(t)| = |f''(t_0)|,
  :label: eq_closed

.. math::
  \Delta t = \sqrt{\frac{8\cdot |e_{tol}|}{|f''(t_0)|}},
  :label: eq_deltat_expdecay

Thus we now avoid the iteration.

Dealing with Non-Decaying Function
----------------------------------
The idea described in Section :ref:`algorithm` sounds plausible, but the assumption is easily broken even when the function :math:`f(t)` is a sum of decaying exponentials with **different sign** of their scale factors, :math:`\alpha_i`, and **different time constant**, :math:`-1/\beta_i`. In this case, there might be some other optimal ways to calculate the time interval :math:`\Delta t` [#]_. However, we simply make :math:`\Delta t` be conservative.

Let's say the function :math:`f(t)` is given by Equation :eq:`eq_analog_response` and each term satisfies Equation :eq:`eq_decaying_fn`. The absoluate value of :math:`f''(t)` is given by 

.. math::
  |f''(t)| = |\sum_{i=0}^N \alpha_i \cdot \beta_i^2 \cdot e^{\beta_i\cdot t}|.
  :label: eq_f2nd

We define a function :math:`g(t)` by taking absolute value of scale factors in Equation :eq:`eq_f2nd`, which is given by

.. math::
  g(t) = \sum_{i=0}^N |\alpha_i \cdot \beta_i^2| \cdot e^{\beta_i\cdot t}.
  :label: eq_g2nd

Equation :eq:`eq_g2nd` is then a decaying function and gives more conservative bound than :eq:`eq_f2nd` by triangular inequality (:math:`|z_1+z_2|\leq |z_1|+|z_2|`). Then, to calculate :math:`\Delta t`, we simply replace :math:`|f''(t_0)|` with :math:`g(t_0)` in Equation :eq:`eq_deltat_expdecay` as follows.

.. math::
  \Delta t = \sqrt{\frac{8\cdot |e_{tol}|}{g(t_0)}}.
  :label: eq_deltat_refine

Note that the basis function should be representing oscillatory behavior as well. Thus, in addition to the decaying exponential function, we also provide two more basis functions; :math:`\alpha_i \cdot cos(\beta_i\cdot t)` and :math:`\alpha_i \cdot e^{\beta_i\cdot t}\cdot cos(\gamma_i \cdot t)`. For these basis functions, we both take the absoluate value of each scale factor and set :math:`cos(\cdot)` to one for conservative :math:`\Delta t` calculation. Then, :math:`g_i(t)`'s are given by

.. math::
  g_i(t) = |\alpha_i \cdot \beta_i^2|,
  :label: eq_gt_cos
.. math::
  g_i(t) = |\alpha_i \cdot (\gamma_i^2 - 2.0\cdot \gamma_i/\beta_i + 1.0/\beta_i^2)|\cdot e^{\beta_i\cdot t},
  :label: eq_gt_expcos

respectively. 

Supported Basis Function
------------------------
There are some more basis functions for PWL approximation. For example, :math:`\alpha_i\cdot t` represents a ramp function and :math:`\alpha_i\cdot t^2` is needed for modeling an integrator of a ramp (PWL) signal. In summary, all the supported basis functions are as follows

+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| Basis Function                                                       | Condition                                                                                                                 | Expression in config.py                                          |
+======================================================================+===========================================================================================================================+==================================================================+
| :math:`\alpha_i`                                                     | :math:`\alpha_i \in \mathbb{R}`                                                                                           | ('const', :math:`\alpha_i`)                                      |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i\cdot e^{\beta_i\cdot t}`                             | :math:`\alpha_i \in \mathbb{R} \; \mathrm{ and }\; \beta_i \in \mathbb{R^-}`                                              | ('exp', :math:`\alpha_i`, :math:`\beta_i`)                       |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i \cdot cos(\beta_i\cdot t)`                           | :math:`\alpha_i \in \mathbb{R} \; \mathrm{ and }\; \beta_i \in \mathbb{R^+}`                                              | ('cos', :math:`\alpha_i`, :math:`\beta_i`)                       |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i \cdot e^{\beta_i\cdot t}\cdot cos(\gamma_i \cdot t)` | :math:`\alpha_i \in \mathbb{R} \; \mathrm{ and }\; \beta_i \in \mathbb{R^-}\; \mathrm{ and }\; \gamma_i \in \mathbb{R^+}` | ('exp*cos', :math:`\alpha_i`, :math:`\beta_i`, :math:`\gamma_i`) |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i\cdot t`                                              | :math:`\alpha_i \in \mathbb{R}`                                                                                           | ('t', :math:`\alpha_i`)                                          |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i\cdot t^2`                                            | :math:`\alpha_i \in \mathbb{R}`                                                                                           | ('t**2', :math:`\alpha_i`)                                       |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| :math:`\alpha_i\cdot t\cdot e^{\beta_i\cdot t}`                      | :math:`\alpha_i \in \mathbb{R} \; \mathrm{ and }\; \beta_i \in \mathbb{R^-}`                                              | ('t*exp', :math:`\alpha_i`, :math:`\beta_i`)                     |
+----------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+

Examples
========

Low Dropout Voltage Regulator
-----------------------------

The figure below shows how the LDO model looks like. The output is essentially a scaled version of the reference voltage input (``vref``). The static transfer function is implemented in ``txf2``, while its output is filtered by a two-pole filter (``filter_p2``). Line regulation (the output dependency on the power supply fluctuation) is also implemented. The static line regulation is described in ``txf1``. The two-pole, and one-zero filter (``filter_p2z1``) represents the power supply rejection behavior of the regulator. The two filtered outputs are combined together by an analog adder. To add them properly, the output of the tranfer curve model (``txf1``) indeed the additive term to the output compared to the supply input (``vin``) is at some DC value.


.. figure:: _static/ldo_model.png
  :width: 300px
  :align: center

  Level 1 model of a LDO regulator.


The transfer functions of all implemented models are shown below.

.. figure:: _static/ldo_txf1.png
  :width: 400px
  :align: center

  Transfer curve of ``txf1`` (``vin`` to ``vout``).


.. figure:: _static/ldo_filter_p2z1.png
  :width: 400px
  :align: center

  Frequency response of ``filter_p2z1`` (poles: [20 MHz,150 MHz], zero: 1 MHz).


.. figure:: _static/ldo_txf2.png
  :width: 400px
  :align: center

  Transfer curve of ``txf2`` (``vref`` to ``vout``).


.. figure:: _static/ldo_filter_p2.png
  :width: 400px
  :align: center

  Frequency response of ``filter_p2`` (poles: [10 MHz, 10 MHz]).

After building the regulator model, we ran transient simulations as well as AC simulations, which are shown below.

.. figure:: _static/ldo_gain.png
  :width: 400px
  :align: center

  Frequency response of a LDO from ``vref`` to ``vout``.

.. figure:: _static/ldo_psrr.png
  :width: 400px
  :align: center

  PSRR (frequency response of a LDO from ``vin`` to ``vout``).


Conclusion
==========

References
==========

Footnote
========
.. [#] This needs more optimization for speed, since the indexing is costly when the size of a lookup table is huge. It can be easily fixed, but I'm lazy for now.
.. [#] For now, we recommend the system's order to be one because of some bug in DC initialization for AC simulation although it looks fine in transient simulation. If your transfer function has more than one pole, we suggest to you cascade two single pole systems.
.. [#] The time step depends on ratio of both scale factors and time constants between additive terms, and there should be a way to optimize the time step (e.g. dominant-pole approximation). Generally, however, thses parameters, scale factors and time constants, could be tunable, which requires some undesirable computations during simulations. 
