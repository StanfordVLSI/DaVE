.. _circuitsim:

*********************
Other Important Setup
*********************

.. _analogcontrol:

Analog Control File for Circuit Simulation
==========================================

When running circuit simulations with *NCVerilog* simulator, one needs to prepare an analog control file which sets up the circuit simulation environment in Spectre. For more information on its syntax, please refer to Cadence AMS Simulator User Guide.

Some information from :ref:`testconfig` and :ref:`simconfig` can be imported into this analog control file. Like :ref:`binding test vectors to Verilog testbench <bindvector>`, this file also adopts `empy <http://www.alcyone.com/software/empy/>`_ templating system. The available binding variables are summarized below.

+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
| Variable name     | Description                                                                                                                                  |
+===================+==============================================================================================================================================+
| temperature       | Circuit simulation temperature. The value of ``temperature`` field in :ref:`test configuration file <testconfig>` will be bounded.           |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
| initial_condition | Initial condition of some nets. The contents of ``[[[initial_condition]]]`` in :ref:`test configuration file <testconfig>` will be bounded.  |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
| spice_lib         | Spice/Spectre model file name. The value of ``spice_lib`` field in :ref:`simulator configuration file <simconfig>` will be bounded.          |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+
| sim_time          | Transient simulation time which is defined in ``time`` field of ``[[simulation]]`` section, explained in :ref:`simulationtime`.              |
+-------------------+----------------------------------------------------------------------------------------------------------------------------------------------+

The following example shows how the binding variables should be declared in the control file.

.. include:: _static/analogcontrol.scs
  :literal:

Testbench Module Name
=====================

The module name of a generated Verilog testbench is always ``test``. You might need this information for setting up some simulation environments. For example, the ``probe.tcl`` file for *NCVerilog* simulator requires this module name to store waveforms. 
  
.. include:: _static/probe.tcl
  :literal:

