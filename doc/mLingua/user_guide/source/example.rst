.. _example:

*******
Example
*******

All the examples are under ``example`` directory.

To run the simulation, there are two options. If you want to save the waveform, do the following ::

  $ make run_wave

If you want to run the simulation without storing the waveform, do the following ::

  $ make run

To clean up the temporary simulation files, do the following ::

  $ make clean

As for simulation performance, all the simulations are performed on Intel i7-3610QM processor (2.30GHz) and the simulator is VCS ``H-2013.06-SP1``.

.. _eg_spf:

Single Pole Filter
==================

A single pole filter model and its relevant simulation setup is available under ``example/single_pole_filter`` directory.


Wavefrom
--------

Here is the captured waveform and its zoomed version. The wave in pink, cyan, and yellow are PWL pulse input, PWL pulse output, the PWL output offset, respectively. The transition of ``wakeup`` signal is the point when the output event occurred.

.. figure:: _static/single_pole_filter.png
  :width: 800px
  :align: center

  Pulse input and its output.

.. figure:: _static/single_pole_filter_zoom.png
  :width: 800px
  :align: center

  Zoomed version of the figure above.

Simulation Performance
----------------------

This shows VCS simulation profile with running 21 msec of transient time with the input pulse period of 140 nsec; Roughly, 150,000 cycles of input clock are exercised. The reported simulation time is about 5 sec. The generated Verilog code is shown here as well.

For comparison, a uniformly-sampled filter version is also implemented. The time step is set to the minimum time step acquired with the generated PWL model which is 240 psec. The same pulse input is applied although the simulation time should be affected by the pulse width as well. The simulation time is about 30 sec which is about 6x slower than the PWL model with non-uniform time step control. The performance profile is also attached at the end of this section

.. include:: _static/vcs.prof.spf
  :literal:

.. literalinclude:: _static/single_pole_filter.v
  :linenos:
  :language: verilog

.. include:: _static/vcs.prof.spf.uniform
  :literal:

.. _eg_pll:

phase Locked Loop
=================

A charge-pump phase locked loop example is available under ``example/phase_locked_loop`` directory. Under the directory, there are three sub-directories; ``model`` which contains all Verilog models, ``sim_lpf`` for simulating loop filter only, and ``sim_pll`` for running a complete pll simulation.

Note on Loop Filter
-------------------

There are various ways to implement this. For example, one can directly model the transfer function of its voltage output :math:`V_{C}` to its step current input :math:`I_{cp}`. In this example, we model the current (:math:`I_1`) through a damping resistor (:math:`R`) and integrating capacitor(:math:`C_1`). The current :math:`I_1` is decomposed into two responses; forced response to the step current input :math:`I_{cp}` and the natural response. The complete response equation for the modeling is given as follows.

.. math::
  I_{1}(t) = I_{cp}\cdot \frac{C_1}{C_1+C_2}\cdot (1.0-e^{-t/\tau}) + \frac{V_{C}-V_{C1}}{R}\cdot e^{-t/\tau}
  :label: eq_I1

.. math::
  \tau = R\cdot \frac{C1\cdot C2}{C1+C2}
  :label: eq_tau

.. math::
  V_{C1}(t) = \frac{1}{C_1}\cdot \int \! I_{1}(t) \mathrm{d}t
  :label: eq_vc1

.. math::
  V_C = V_{C1} + I_{1}\cdot R
  :label: eq_vc

.. figure:: _static/lpf.svg
  :width: 300px
  :align: center

  Schematic diagram of loop filter.

To handle the natural response of the system, we modify the Verilog code after generating a skeleton code; modeling the forced response (:math:`I_1` vs :math:`I_{cp}`). You could see how the modification is made by comparing two models, ``example/phase_locked_loop/model/lpf.v`` and ``example/phase_locked_loop/model/lpf_generated.v``.

Waveform
--------

The loop filter output voltage (:math:`V_{C}`) during the locking process is shown in the figure below.

.. figure:: _static/pll_locking.png
  :width: 800px
  :align: center

  Loop filter voltage during the PLL locking process.

Loop Filter Code
----------------

.. literalinclude:: _static/lpf.v
  :linenos:
  :language: verilog


Simulation Performance
----------------------

The below is the performance summary of the simulation using VCS ``H-2013.06``. The PLL takes 2.1 GHz clock input and produces the same clock output frequency. The transient simulation time is set to 50 usec. The report shows that it runs in about 1.4 sec.

A uniformly sampled models (1 ps, 10 ps, and 100 ps time step) is also tested, resulting in 11x, 2.3x, 1.1x slower performance (16.4 sec, 3.1 sec, 1.51 sec), respectively.


.. include:: _static/vcs.prof.pll
  :literal:

Short Note on XMODEL
--------------------

For performance comparison, a phase-locked loop in XMODEL is tested with all jitter modeling off. [1]_ The simulation time is about 86 sec (54x slower than PWL example). Verilog DPI and PLI calls spend most of the simulation time. 

Circuit vs Verilog Simulation
-----------------------------

The simulation performance comparison between circuit simulation and Verilog simulation is also performed. Since the available PLL circuit has different parameters (e.g. R, C1, C2, VCO gain, etc), we adjusted the model parameters as well. For example, the PLL takes 500 MHz clock input and procduces 1 GHz clock. The transeint time of the simulation is set to 20 usec. Here is the run-time comparison.

  - Verilog runtime: 0.4 sec
  - Circuit runtime: 7659 sec
  - Performance gain: 19147x


.. [1] Of course, the model is not optimized completely and thus the comparison is somewhat unfair.

