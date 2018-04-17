*******************************
Introduction to *mProbo* [#]_
*******************************

Today it is difficult to validate a mixed-signal System-on-Chip, i.e., one which contains analog and digital components.  The problem is that the analog and digital subsystems are usually strongly intertwined so they must be validated together as a system, but the validation approach for analog and digital blocks are completely different.  We address this problem by creating high-level functional models of the analog components that are compatible with top-level digital system validation, and then providing a method of formal checking to ensure that these functional models match the operation of the transistor level implementations of these blocks.

Behavioral modeling of analog circuits in either (System)Verilog or Verilog-AMS has been widely used for mixed-signal SoC verification more than a decade as the two subsystems, analog and digital, are more tightly coupled. For example, the coefficients of a decision feedback equalization block in high-speed links are calibrated and compensated in digital domain. Since such calibration loop has a large time constant, it is inefficient to run it in co-simulation environment, i.e. circuit simulator for analog and event-driven simulator for logic. Thus, analog designers generate schematics/layouts of their circuits and verify them using SPICE-like simulators. The corresponding models are written by either analog designers or verification engineers and are used for chip-level verification with digital RTL models. 

Yet, such verification methodology with analog functional models are not accepted as a de-facto standard, since the methodology creates another problem. That is, there is a chance that the verification of a SoC design has passed, but its fabricated chip does not function. The root cause of such failures is that the correspondence between a circuit and its model is not checked.

*mProbo* is a software tool to check the functional equivalence of analog circuits in any two representations. In particular, this tool is initially designed to check between a transistor-level implementation of an analog circuit and its description in SystemVerilog. 

Supported Model Languages
=========================

A model can be either a (system-)Verilog model or a Verilog-AMS. Note that a transistor netlist is a subset of a Verilog-AMS model.

Supported Simulators
====================

Both Synopsys' *VCS* and Cadence' *INCISIVE-simulator* are supported for (System)Verilog model simulation. For Verilog-AMS, only Cadence' *INCISIVE-simulator* is supported. In the near future, Synopsys' *CustomSim* will be supported for Verilog-AMS as well.

.. [#] Most of this section is excerpted from `Dr. Lim's thesis <http://purl.stanford.edu/xq068rv3398>`_ .
