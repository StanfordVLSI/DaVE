.. _testconfig:

******************
Test Configuration
******************

A test configuration file describes the needed test(s) for model checking. Like :ref:`simconfig`, its syntax also follows `ConfigObj <http://www.voidspace.org.uk/python/configobj.html>`_.

Overview
========

A section name at the first level (``[ ]``) is a test name. For example, the following section defines a test named ``test1``. ::

  [test1]

Under this section, you can write essential components of a test, which will be described in the rest of this section.

The following skeleton code shows the structure of a test configuration. All the components describing a test are the sections at the second level (``[[ ]]``) except ``description`` fields. ::

    [test1] # a test named "test1"

      description = ''' ... ''' # description of "test1"

      [[port]] # port specification of "test1"
        ...
      [[testbench]] # testbench of "test1"
        ...
      [[simulation]] # simulation time control of "test1"
        ...
      [[option]] # test control options

    [test2] # another test named "test2"
      ...

There are two essential components in a test; port specification, testbench. Port information such as the type and valid range of a signal should be specified in ``[[port]]`` section. The ``[[testbench]]`` section sets up actual test components to run simulations. Test vectors generated from the port specification, and each vector is put to the embedded Verilog(-AMS) testbench in ``[[testbench]]`` section.

The output responses of a device-under-test can be directly measured by probing signals at the output ports. In some cases, however, responses (e.g. gain, pole, swing, etc.) are not the direct outputs being measured from pins. These can be indirectly measured through post-processing output signals. Thus post-processing scripts if needed should be specified in the test configuration. Rather than embedding the scripts, the location and command to run the scripts is declared in a test configuration, which is a subsection ``[[[post-processor]]]`` of ``[[testbench]]`` section. An example is shown below. ::

    [[[post-processor]]]
      script_files = ${DAVE_SAMPLES}/util/postprocessor/filter_estimator.py
      command = python filter_estimator.py 1e6 10e9 p1

While running a checking, script files will be copied to each simulation directory and the command will be executed after running Verilog(-AMS) simulation.

After extracting all the responses from simulations, the responses are fitted to abstraction models by running linear regressions. The section ``[[option]]`` sets some options to control linear regression as well as test vector generation.

``[[simulation]]`` section specifies the information related to simulation time. This sets up the time unit and precision of the Verilog simulation as well as transient simulation time.

Note that, like :ref:`simconfig`, one can define a ``[DEFAULT]`` section which will be applied to all the tests in the same configuration file. Then, each test can override the default test.

An example of a test configuration is shown below.

.. include:: _static/test.cfg
  :literal:

Test Description
================

There is a variable ``description`` right under the test section.

+-------------+----------------------------------------------------------------+
| Variable    | Description                                                    |
+=============+================================================================+
| description | | Description of a test. You may want to use Python's          |
|             | | multiline string with triple-quotation marks (''').          |
|             | | This field is optional.                                      |
+-------------+----------------------------------------------------------------+

Writing Port Specification
==========================

First of all, keep in mind that the terminology *port* has different meaning from a physical *pin*. The *port* is a signal input/output of an abstract system model, while *pin* is a physical input/output of a circuit entity. For example, a phase-locked loop has an input pin to feed a reference clock which is typically a voltage signal. A PLL can be mapped to a linear system model in phase domain in which the corrresponding *port* of the clock input pin in phase domain can be defined. There is also an output pin of a PLL from which a generated clock comes out. Again, an output *port* in phase domain corresponds to the output pin in a phase-domain PLL model.

Back into the port specification, we categorize ports of a mixed-signal circuit into a few subtypes depending on the intent of a port, and its signal data type in a transformed variable domain [#]_, which is summarized in the table below.

+-----------------+---------------------+------------------------+
| Signal Datatype | Port Type           | Description            |
+=================+=====================+========================+
| Real            | AnalogInputPort     | Analog (control) input |
|                 +---------------------+------------------------+
|                 | AnalogOutputPort    | Analog (pseudo) output |
+-----------------+---------------------+------------------------+
| Bit Vector      | QuantizedAnalogPort | Quantized analog input |
|                 +---------------------+------------------------+
|                 | DigitalModePort     |  True digital input    |
+-----------------+---------------------+------------------------+

In ``[[port]]`` section, port names are specified at the third level (``[[[ ]]]``) where their properties are assigned. The following example is a skeleton code to define specifications of ports. ::

    [[port]]
      [[[port name 1]]]
        port property 1 = value1
        port property 2 = value2
        ...
      [[[port name 2]]]
      ...

The following two subsections describe port properties.

Analog Port Properties
----------------------
An analog port (``AnalogInputPort`` and ``AnalogOutputPort``) has the following properties.

+---------------+------------------------------------------------------------------------------------------------------+---------------+
| Property      | Description                                                                                          | Default value |
+===============+======================================================================================================+===============+
| port_type     | Either ``analogoutput`` for *AnalogOutputPort* or ``analoginput`` for *AnalogInputPort*.             |               |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| regions       | | Two numbers (separated by ``,``), which are lower/upper bounds of a signal.                        |               |
|               | | See also :ref:`pwls` for extended use.                                                             |               |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| pinned        | | ``AnalogInputPort`` only. The value of this input port is set to the value in                      | False         |
|               | | ``default_value`` property for all test vectors if ``pinned`` is set to ``True``.                  |               |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| default_value | ``AnalogInputPort`` only. Default signal value when ``pinned`` flag is set to ``True``.              |               |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| abstol        | ``AnalogOutputPort`` only. The threshold of the residual error and offset value of the fitted model. | 1.0           |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| gaintol       | ``AnalogOutputPort`` only. The threshold in [%] of gain error.                                       | 25            |
+---------------+------------------------------------------------------------------------------------------------------+---------------+
| description   | Description of a port.                                                                               |               |
+---------------+------------------------------------------------------------------------------------------------------+---------------+


Digital Port Properties
-----------------------
A digital port (``QuantizedAnalogPort`` and ``DigitalModePort``) has the following properties.

+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| Property        | Description                                                                                        | Default value |
+=================+====================================================================================================+===============+
| port_type       | Either ``quantizedanalog`` for *QuantizedAnalogPort* or ``digitalmode`` for *DigitalModePort*.     |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| bit_width       | Bit width of the port.                                                                             |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| encode          | Code encoding style. Choose one of ``thermometer``, ``binary``, ``gray``, ``onehot``.              | binary        |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| prohibited      | | a comma-separated list of prohibited codes. Supported expression is to use either an integer     |               |
|                 | | (e.g. 3, 5) or a binary number with the prefix ``b`` (e.g. b101, b011). The intrinsic prohibited |               |
|                 | | codes depending on ``encode`` property are automatically added to this list.                     |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| pinned          | | The value of this input port is set to the value in ``default_value`` property for all test      | False         |
|                 | | vectors if ``pinned`` is set to ``True``.                                                        |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| default_value   | | Default signal value when ``pinned`` is ``True``. The expression is the same as ``prohibited``   |               |
|                 | | (i.e. either an integer or a binary with ``b`` prefix).                                          |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+
| description     | Description of a port.                                                                             |               |
+-----------------+----------------------------------------------------------------------------------------------------+---------------+

Writing an Embedded Testbench
=============================

While users might want to have separate testbench files for two circuit entities being compared, we only allow embedding a testbench in the configuration to prevent any possible inconsistency/error in two testbenches. Thus we'd like to ensure that golden and revised models share the same testbench.

One would write a testbench in ``testbench`` section to run circuit/model simulations with given test vectors. In general, there are two essential parts in a testbench: 1) *instance* such as stimulus drivers to feed signals to a DUT (Device-Under-Test), a DUT itself, and measurement modules to strobe the output responses of the DUT, 2) *wire* declaration to interconnect instances. While the earlier version of the checker tool had a specific format to write the parts, the format is more liberal in the latest version, which has the following structure. ::

    [[testbench]]
      tb_code = '''

      ''' # add multiline, custom testbenches enclosed by two, triple-quotation marks.
      [[[wire]]] # subsection describes wires
        ...

In ``tb_code`` field, test instances will be written in Verilog format and wires are declared in ``wire`` subsection. From this description, either a Verilog-AMS or a Verilog testbench is generated --- a Verilog-AMS testbench is to run an AMS model and a Verilog testbench is to do a Verilog model. This implies that it is strongly recommended for all the instances described in this ``tb_code`` section to have one-to-one correspondence between Verilog and Verilog-AMS. For example, let's say a pulse generator module is instantiated. Two pin/parameter-accurate Verilog and Verilog-AMS module of the pulse generator should be available since a simulator would call either Verilog-AMS module and Verilog module depending on the type of DUT model (e.g. circuit netlist vs. Verilog). Of course one could use a simulation directives (e.g. \`ifdef AMS/ {do something} \`else {do another} \`endif) to selectively instantiate the modules or perform a certain function. However, this is error-prone as explained above.

Circuit temperature
-------------------

While it is possible to set simulation temperature directly in :ref:`analogcontrol`, it is recommended to put it in a test configuration. This is because temperature could be an input port to a system in some test. For example, one might verify how an output voltage varies with temperature in a bandgap reference circuit. Thus ``temperature`` field under ``[[testbench]]`` section is provided. For example, the example below binds *temperature* input port to a testbench ::
  
  temperature = @temp # temp is an analog input port


Wire
----

An Verilog/-(AMS) module always includes *wire* declaration to explicitly declare the signal discipline of a wire. For example, the signal on a wire could be an analog signal, ``real`` in Verilog, or an digital signal, ``logic`` or ``wire`` in Verilog.

The ``wire`` data type of a Verilog-AMS is extended from Verilog, and there are some difference in declaring wires between two languages. The wire declaration of the checker, therefore, has the following format. ::

    [[[wire]]]
      ams_electrical = ...
      ams_wreal = ...
      ams_ground = ...
      logic = ...

And, the following table shows the reserved wire definitions and how they are mapped to Verilog/(-AMS) language.

+-----------------+---------+-------------+
| Reserved wire   | Verilog | Verilog-AMS |
+=================+=========+=============+
| ams_electrical  | real    | electrical  |
+-----------------+---------+-------------+
| ams_wreal       | real    | wreal       |
+-----------------+---------+-------------+
| ams_ground      |  N/A    | ground      |
+-----------------+---------+-------------+
| logic           | wire    | wire        |
+-----------------+---------+-------------+

Of course, it is also possible to declare user-defined wires. For example, a signal is represented using a piecewise linear (PWL) waveform approximation. Other than the default wire definition above, the tool assumes that a user prepare a macro for custom wires to switch the datatype in Verilog and in Verilog-AMS. For example, suppose that one declared the wire ``vctrl`` in ``pwl_wire`` datatype as follows ::

    [[[wire]]]
      pwl_wire = vctrl

In the generated Verilog(-AMS) testbenches, this declaration is then appeared as follows ::
 
    `pwl_wire vctrl;
    
To compile the above statement correctly, the definition of the user's macro ```pwl_wire`` should be included during the simulation, which might have the form like this ::

    `ifdef AMS     // if it runs AMS
      `define pwl_wire electrical
    `else          // if it runs SystemVerilog
      `define pwl_wire pwl
    `endif

where ``pwl`` is a user-defined datatype (e.g. using *struct* in SystemVerilog) to represent PWL waveform.

Lastly, it is also possible to directly declare wires in ``tb_code`` field. However, it is suggested to utilize ``wire`` subsection since *wire sanity check* is done only for the wires defined the subsection. 

Strobing Response
-----------------

Once a simulation is performed, the output response shall be sampled and mapped to the corresponding output port defined in ``[[port]]`` section. In this checker, the mapping is done through a file. That is, the response must be saved to a file in a particular filename format, and the tool reads the file. The file naming rule for the measurement is ``meas_%s.txt`` where the string is the output response name. For instance, one would write a Verilog(-AMS) measurement module (instantiated in ``tb_code`` field) which strobes a signal at a particular time and store the strobed value to a file. In the measurement module, the strobe time and the filename are parameterized and the strobed signal is the input to the module. 

In the example below, the measurement module *dump_v* will sample the voltage difference of two signals, ``out_smpl`` and ``gnd``, at 3.79 ns and store the value to the file ``meas_vout.txt``. Then, the tool reads out the value in the file and map it to the output response of ``vout`` port.

  dump_v #(.ts(3.79e-9), .filename("meas_vout.txt"))  meas_vout ( .pn(out_smpl), .nn(gnd) );


.. _initcond:

Initial Condition
-----------------

For circuits like a switched-capacitor integrator, initial state(s) of node(s) should be considered. Initial values of nodes at time=0 sec in running simulation can be assigned in ``[[[initial_condition]]]`` subsection of ``[[testbench]]`` section. For example, if you want to set ``node_m`` of an instance ``dut`` to 0.5 [V] ::

  [[testbench]]
    ...
    [[[initial_condition]]]
      dut.node_m = 0.5

Sometimes, state names might be different between *golden* and *revised* models. In this case, one can create either ``[[[[golden]]]]`` or ``[[[[revised]]]]`` subsection under ``[[[initial_condition]]]`` section like this. ::

  [[testbench]]
    ...
    [[[initial_condition]]]
      dut.node_m = 0.5 # common to both golden and revised models
      [[[[golden]]]]
        dut.node_s = 0.1 # applies to only golden model
      [[[[revised]]]]
        dut.node_s1 = 0.11 # applies to only revised model

Lastly, a state can be an input port to a system. Therefore, one can bind the test vector of the port to an initial condition like this. ::

    [[[initial_condition]]]
      dut.node_m = @vout_state # vout_state is an analog input port


Post Processing Routine
-----------------------

Sometimes, an output being measured is not the direct output of a circuit, but needs a post-processing routine of simulation data. For example, pole frequencies of a system can be extracted by post processing a step response of a system. In a Verilog testbench, an output waveform is sampled at regular intervals and the sampled data are stored to a file. Then, a post-processing script is executed to estimate the transfer function of a system to get pole frequencies. 

Calling a post-processing script can be done in ``[[[post-processor]]]`` subsection under ``[[testbench]]`` section as follows. ::

    [[[post-processor]]]
      script_files = ... # comma-separated list of script files
      command = ...      # shell command to perform post-processing

The checker will copy the script files into simulation directory and execute the shell-command written in ``command`` field. To correctly map the result of post-processing routine(s) to an output response (port), the result should be stored in a file which has a naming rule of ``meas_%s.txt`` where the string is the output response (port) name. The table below is a summary of fields in ``[[[post-processor]]]``.

+-----------------+------------------------------------------------------------+
| Property        | Description                                                |
+=================+============================================================+
| script_files    | | List of user-provided script file names being copied     |
|                 | | to simulation directory.                                 |
+-----------------+------------------------------------------------------------+
| command         | Shell-command to perform post-processing.                  |
+-----------------+------------------------------------------------------------+

In the example below, a script file *${DAVE_DEMO}/lpf/estimate_pole_freq.py* which estimates a pole frequency from a step response will be copied to a simulation directory, and the command *python estimate_pole_freq.py* will be executed to run the script and the estimated pole frequency is stored in ``meas_pole.txt`` (filename is set in *estimate_pole_freq.py*) given that the corresponding output port name is ``pole``. ::

    [[[post-processor]]] 
      script_files = '${DAVE_DEMO}/lpf/estimate_pole_freq.py'  
      command = 'python estimate_pole_freq.py' 


.. _bindvector:

Binding Test Vector to Testbench
================================

Once you prepared a test configuration file, the checker tool read it and generate intermediate testbenches for both ``golden`` and ``revised`` models. For each test vector, the generated vector will be put to the intermediate testbenches to run simulations for both models. 

To bind a test vector to an intermediate testbench, there should be some notion where to put the test vector, which follows `empy <http://www.alcyone.com/software/empy/>`_ format. Basically, you should put ``@`` followed by an input port name in an embedded testbench to bind a test vector value. For example, the following code shows how a test vector for ``sel_iq`` port is bound to the parameter ``value`` of the instance ``xdrv_sel_iq`` which generates 12-bit logic value. ::

    [test1]
      ...
      [[port]]
        [[[sel_iq]]]
          port_type = quantizedanalog
          bit_width = 12
          encode = thermometer
          pinned = True
          default_value = b111111000000
        ...
      [[testbench]]
        ...
        tb_code = '''
        bitvector #( .value(@sel_iq), .bit_width(12) ) xdrv_sel_iq ( .out(sel_iq) );
        ....
        '''

And, the bounded testbench for a specific test vector (e.g. ``sel_iq=4032``) will look this in a final testbench. ::

    bitvector #( .value(4032), .bit_width(12) ) xdrv_sel_iq ( .out(sel_iq) );

.. _simulationtime:

Simulation Time Control
=======================

Users should provide time related information such as time unit/precision and simulation time. Simulation time control in a test starts at the section ``[[simulation]]`` like this ::

    [[simulation]]      # simulation time control
      timeunit = 1ps    # Verilog-compliant time unit/ time precision 
      trantime = 1.2ns  # transient time

The following subsection describes the properties of the simulation time control.

Properties  
----------

+-------------+-----------------------------------------------------------------------------------------+
| Property    | Description                                                                             |
+=============+=========================================================================================+
| timeunit    | Time unit/precision of a simulation. This follows the rule of Verilog timescale option. | 
+-------------+-----------------------------------------------------------------------------------------+
| trantime    | Transient time of a test.                                                               |
+-------------+-----------------------------------------------------------------------------------------+

Test Control Option
===================

There are options to control a test such as vector generation and linear model extraction, etc. For example, after exercising all the test vectors in a test, the tool run linear regression analysis on the sampled responses with respect to test vectors to extract a linear system model of a DUT (Device-Under-Test). The runtime option of this analysis can be controlled in ``[[option]]`` section.

Properties  
----------

Here are properties valid for ``option`` section.

+-----------------------------+--------------------------------------------------------------------------------+---------------+
| Property                    | Description                                                                    | Default value |
+=============================+================================================================================+===============+
| max_sample                  | | Maximum number of test vectors to be excercised. The tool also internally    | 3             |
|                             | | calculates the minimum number of required test vectors and select the larger |               |
|                             | | number between the two. Note that the tool stops exercising test vectors if  |               |
|                             | | an error is detected before running all the prepared test vectors.           |               |
+-----------------------------+--------------------------------------------------------------------------------+---------------+
| regression_order            | Maximum polynomial order of a regression model                                 | 1             |
+-----------------------------+--------------------------------------------------------------------------------+---------------+
| regression_en_interact      | Include the first order interaction terms between inputs in linear models      | True          |
+-----------------------------+--------------------------------------------------------------------------------+---------------+
| regression_sval_threshold   | Normalized input sensitivity threshold value in % to suggest a model.          | 5             |
+-----------------------------+--------------------------------------------------------------------------------+---------------+

Predictor Exclusion  
-------------------

While an extracted linear model includes all the inputs by default, you may sometimes want to exclude some inputs from predictor variables of a linear regression model. In this case, you can manually exclude the inputs by declaring ``[[[do_not_regress]]]`` subsection under ``[[option]]`` section like this example. ::

    [[option]]
      ...
      ...
      [[[do_not_regress]]]
        out1 = ina, inc
        out2 = inb

In the example, linear regression will exclude ``ina`` and ``inc`` inputs for ``out1`` output, and ``inb`` input for ``out2`` output, respectively.

User-Defined Model
------------------

It is possible to fit the response to a specific linear regression model. This user-defined regression model is specified in the subsection ``[[[regression_user_model]]]`` under the section ``[[option]]``. The skeleton code looks like this ::

  [[option]]
    ...
    [[[regression_user_model]]]
      output1 = ... # user-defined regression model of output1

An example snippet looks as follows. ::

  [[[regression_user_model]]]
    dcout = dcin + avdd + avdd:sel_p_2 + avdd:sel_p_1 + avdd:sel_p_0 + avdd:sel_n_2 + avdd:sel_n_1 + avdd:sel_n_0 

Note on Model Expresion
^^^^^^^^^^^^^^^^^^^^^^^

It is useful to understand on how to write your own regression model. Basically, the model expression follows the statistical package `R <http://cran.r-project.org/>`_. The below is a basic usage of the expression.

+------------+-------------------------------+
| expression |                               |
+============+===============================+
| x0         | predictor variable x0         |
+------------+-------------------------------+
| x1         | predictor variable x1         |
+------------+-------------------------------+
| x0 + x1    | a simple linear model         |
+------------+-------------------------------+
| x0:x1      | product of x0 and x1          |
+------------+-------------------------------+
| x0*x1      | equivalent to x0 + x1 + x0:x1 |
+------------+-------------------------------+
| I(x0**n)   | nth power of x0               |
+------------+-------------------------------+

When the quantized port is expanded, the tool generates a new name for each bit of the port, which follows the naming convention ::

  %s_%d where %s is the port name, %d is an integer corresponds to nth bit 
  
For example, there exists a 2-bit, quantized analog port ``sel_n``, i.e. ``sel_n[1:0]``. Then, the new predictor names for the expanded quantized port model is ``sel_n_1`` and ``sel_n_0``.

.. _pwls:

Piecewise Linear Segmentation
=============================

In some case, the circuit's response is still smooth yet strongly nonlinear. This tool supports piecewise linear segmentation of analog input space. Every analog input port (*AnalogInputPort*) could have multiple regions by listing more than two numbers in ``regions`` field. For example, if ``regions = 0.0, 0.5, 1.0``, the tool generate two separate tests from the original test; one of the tests has ``regions = 0.0, 0.5`` and the other has ``regions = 0.5, 1.0``. 

If there are multiple ports which have multiple regions, the tool generates multiple tests by accounting for the cross-product of multiple regions. The generated tests then have test names of ::

  %s_%d where %s is the original test name, %d is an integer 

For example, in ``test1``, if there are two ports where one has two regions and the other has five regions, the tool generates 10 (2 by 5) regions and the corresponding test names are from ``test1_0`` to ``test1_9``.

.. [#] `My PhD thesis <http://purl.stanford.edu/xq068rv3398>`_ describes this concept in great detail.
