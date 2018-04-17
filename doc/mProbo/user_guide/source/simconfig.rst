.. _simconfig:

***********************
Simulator Configuration
***********************

The *mProbo* is a simulation-based tool; it extracts the abstraction models of two circuit representations by running simulations. It means that a proper simulation setup is necessary, which shall be described in a simulator configuration file. For example, the configuration file contains the information on the location of circuit netlists, types of Verilog(-AMS) simulators, simulator-specific options, and so on.

The syntax of this configuration file follows `ConfigObj <http://www.voidspace.org.uk/python/configobj.html>`_. [1]_

Terminology
===========

1. ``AMS(Analog Mixed-Signal)`` includes both Verilog-AMS and circuit netlists unless explicitly stated.
2. ``Verilog`` means SystemVerilog unless explicitly stated.

Short Note on Configuration syntax
----------------------------------

1. Assign a variable: You can simply assign a value to a variable with *=*. For example, *Y = X* assigns a value, *X*, to a variable, *Y*.

2. String interpolation with *%(variable)s*: For example, in the following statement, *process_file* is set to "/home/mProbo/est/ckt_env/process.cfg by interpolating a string variable *ex_dir* ::

    ex_dir = /home/mProbo
    process_file = %(ex_dir)s/test/ckt_env/process.cfg

3. Referring to system environment variable with *${}*: For example, the following refers to the system environment variable, *AMSCHECKER_ROOT*. ::

    ex_dir = ${AMSCHECKER_ROOT}/works/examples/ssadc
   
   This environment variable is not interpolated in the original configuration file format (`ConfigObj <http://www.voidspace.org.uk/python/configobj.html>`_). However, *mProbo* will do the interpolation.
  
4. List separator is a comma ``,``

Configuration File
==================

The following subsections describe the content in a simulator configuration file.

Configuration Example
---------------------

.. include:: _static/sim.cfg
  :literal:


Section
-------

The configuration consists of these three sections: *golden*, *revised*, and *DEFAULT*. We name a model as *golden* and the other model as *revised* as we compare two models. The *golden* and *revised* sections will set up their model simulation environments, respectively. Some environment variables might be common to both *golden* and *revised* models. In this case, the common setup can be placed in  *DEFAULT* section [2]_. Note that the *DEFAULT* section name is case-sensitive.

.. _simcfg_rsvd:

Reserved Variable Name
----------------------

There are *reserved words*, key variables for the simulation setup in the *golden* and *revised* sections. Some of the required variables are different depending on the type of the models, ``ams`` or ``verilog``. 


+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| Variable name         | Description                                                                                                                                                                                                                                                                                                            | Model         | Simulator |
+=======================+========================================================================================================================================================================================================================================================================================================================+===============+===========+
| model                 | Select a model: "ams" for AMS or "verilog" for Verilog.                                                                                                                                                                                                                                                                |               |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| simulator             | Choose a simulator: either "ncsim" or "vcs". For AMS simulation, the tool supports only Cadence's NCVerilog ("ncsim") simulator for now.                                                                                                                                                                               | ams / verilog |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| simulator_option      | simulator specific options.                                                                                                                                                                                                                                                                                            | ams / verilog |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| hdl_files             | a comma-separated list of Verilog(-AMS) files.                                                                                                                                                                                                                                                                         | ams / verilog |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| hdl_include_files     | a comma-separated list of Verilog(-AMS) files to be included in a testbench using \`include directive. Note that ``disciplines.vams`` and ``constants.vams`` are automatically included in AMS simulation.                                                                                                             | ams / verilog |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| sweep_file            | Sweep all successful run_script/testbench/measurement files if this is set to True.                                                                                                                                                                                                                                    | ams / verilog |           |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| ams_control_file      | Circuit simulation control file like ``.scs`` file for Spectre if needed. This will be the argument of NCVerilog simulator option, ``+NCANALOGCONTROL+``.                                                                                                                                                              | ams           | ncsim     |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| spice_lib             | File name of SPICE or SPECTRE model library: The value will be plugged into ``@spice_lib`` field (if exists) in the circuit simulation control file, defined in "ams_control_file".                                                                                                                                    | ams           | ncsim     |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+
| default_ams_connrules | Set default wire-from/to-electrical connect rules. For example, we provide a 1.2V logic interface rule, ``connectLib.conn_1p2v``. Note that this field could be left blank and the rule can be assigned directly using ``+amsconnrules+`` in ``simulator_option`` field (e.g. ``+amsconnrules+connectLib.conn_1p2v``). | ams           | ncsim     |
+-----------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------+-----------+

As for ``simulator_option``, some simulator options are automatically included by the tool and duplicate use of some option might cause a simulation fail. The internally generated simulator options are as follows.

+-----------+-----------------------------------------------------------------------------------+
| Simulator | Generated option                                                                  |
+===========+===================================================================================+
|    VCS    | ``-sverilog``, ``-top``, ``-timescale``, ``-debug_pp``                            |
+-----------+-----------------------------------------------------------------------------------+
| NCVerilog | ``+NCTOP+``, ``+NCTIMESCALE+``, ``CLEAN``, ``+NCUPDATE``, ``-SV``,                |
|           | ``+NCAMS``, ``+DEFINE+AMS``, ``+NCANALOGCONTROL+``, ``NCPROPSPATH+``              |
|           | , ``+amsconnrules+``, ``+NCINPUT+hdl.tcl``                                        |
+-----------+-----------------------------------------------------------------------------------+

Note that 
  
  - ``+amsconnrules+`` will be automatically added to ``simulator_option`` only when ``default_ams_connrules`` field in :ref:`simcfg_rsvd` exists in a simulator configuration file,
  - ``+NCINPUT+hdl.tcl`` means that hdl.tcl will be automatically generated in a simulation directory, which looks like this. ::

      # probe tcl for ncsimulator
      database -open test.shm -into test.shm -default
      probe -creat -shm -all -depth all
      run
      exit


Circuit Netlists
----------------

If a golden and/or revised model need(s) some circuit netlist(s), each model section may contain a subsection, ``[[circuit]]``. The variables in the subsection are sub-circuit names and their values are the filenames of circuit netlists which contain the sub-circuit definitions. For example, one wants to run *mProbo* with ``pll`` circuit located in ``/home/johndoe/netlist/pll.sp`` and this circuit corresponds to *golden* model, simply declare the *circuit* subsection like this :: 

  [golden]
    ...
    [[circuit]]
      pll = /home/johndoe/netlist/pll.sp

For standard Verilog simulation, Synopsys' *VCS* and Cadence's *NCVerilog* are supported. For AMS simulation, only *NCVerilog* is supported. 

Note on GUI Environment
=======================

When reading a configuration in the GUI application, the string interpolation is automatically performed. The *DEFAULT* section will disappear in the application while its contents will be reflected on both *golden* and *revised* section.

.. [1] A Python-based interpreter to create both simulator configuration (:ref:`simconfig`) and test configuration (:ref:`testconfig`) will be provided in the future release.
.. [2] For some reason, the section name, *DEFAULT*, should be upper case. 
