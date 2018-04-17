***************************
Generation of Analog Filter 
***************************

We provide a simple script (``genpwl.py``) to generate a single-pole analog filter model in SystemVerilog. If one wants to build a more complicated model such as a loop filter of a PLL explained in :ref:`eg_pll`, the generated code can serve as a skeleton code as well.

Environment Setup
=================

Here is a sample environment setup.

.. include:: _static/setup.cshrc
  :literal:

Running Filter Generator
========================

You can invoke the generation script by typing ``genpwl.py``, and ``genpwl.py -h`` shows its usage like this. Running this script will generate a Verilog file (.v) where its filename without the file extension is the same as its module name.

.. include:: _static/genpwl_help.txt
  :literal:


Writing Configuration File
==========================

To generate a filter model, one needs to provide a configuration file (default name: ``config.py``) which follows Python code syntax. Here is a sample ``config.py`` which is self-explanatory.

.. literalinclude:: _static/config.py
  :linenos:
  :language: python

Generated Verilog Model Example
===============================
Here is the generated single-pole filter model with the configuration file above.

.. literalinclude:: _static/single_pole_filter.v
  :linenos:
  :language: systemverilog


SystemVerilog Include File
==========================
There is the include file in SystemVerilog, which contains some basic type definitions and functions. Here shows the content.

.. literalinclude:: _static/mLingua_pwl.vh
  :linenos:
  :language: systemverilog

Future Work
===========
1. One could gain more speedup by making a lookup table of time-interval instead of calculating at each time. This seems to be possible only if the error tolerance is relative, not absolute. This lookup table method will be implemented in near future.
2. To find a expression for the "response_function" in time domain could be a hassle. A utility to generate time domain expression from a s-domain one will be implemented.
