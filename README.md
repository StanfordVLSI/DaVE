# DaVE

## Overview
Today it is difficult to validate a System-on-Chip which contains analog components (is mixed signal). The problem is that the analog and digital subsystems are usually strongly intertwined so they must be validated as a system, but the validation approaches for analog and digital blocks are completely different. We address this problem by creating high-level functional models of analog components, which is compatible with top-level digital system validation, and then provide a method of formal checking to ensure that these functional models match the operation of the transistor level implementations of these blocks.
 
We provide a set of methodologies and tools for this analog functional modeling, the core part for enabling our Digital Analog Design. Our modeling methodology consists of three core technologies:
 
* mLingua: modeling language in SystemVerilog
* mProbo: model checker
* mGenero: model generator

## mLingua: Event-Driven Piecewise Linear Modeling in SystemVerilog
Real number modeling of analog circuits has become more common as a part of MS-SoC validation. However, such analog models are not accepted as a de facto standard for MS-SoC validation since the models are still believed to be an approximation of their transistor implementations. We address this problem by creating fast, high-fidelity analog functional models completely written in native SystemVerilog language. We leverage a PWL waveform approximation to represent analog signals.
 
This modeling work is further improved by providing a way to dynamically schedule the events for approximating the signal waveform to PWL segments with a well controlled error bound. This dynamic scheduling of events eliminates the need to manually find the largest time step that gives acceptable accuracy, and improves simulation performance.   

## mProbo: Analog Model Equivalence Checking
Creating an analog functional model does not completely solve the validation problem. The models are often provided without checking if their functional behavior matches that of the corresponding circuit implementations, which leads to mixed-signal design errors. Digital designers control system validation and they trust analog models because they believe the model is the specification. Thus, although the chip validation with the models has passed, the real chip could fail because of inconsistencies between analog circuits and their models. The cause of these errors is usually not a subtle analog issue such as nonlinearity and noise — these are found through circuit simulations. Rather, the problems are often trivial wiring mistakes: inconsistencies between circuits and models at the I/O boundary, which include missing connections, mislabeled pins, signal inversion, bus-order reversal, and bus-encoding mismatch. For example, the polarity of a signal might be inverted, e.g., active low vs. active high for the reset signal, and a bus might be connected via different encoding styles, e.g., big-endian vs. little-endian. Worse yet, these errors are often repeated, which is extremely wasteful. We need a functional equivalence checking between an analog circuit and its model to ensure the analog model matches the circuit.
 
The formal checking of the analog blocks is enabled by observing that the result surface of an analog block is a smooth function of its analog inputs -- that is what makes it an analog block. This means it is not difficult to "explore" the design space of an analog block. We use this insight to create an equivalence checker between two analog descriptions: a SPICE netlist and its Verilog model. Our AMS equivalence checker exploits the linear intent of analog circuits. In addition, analog test vector generation along with the intent of I/O ports in AMS designs is automated.

## mGenero: Analog Functional Model Generation/Validation
Our model generation framework provides a way to generate and validate analog functional models in SystemVerilog from templates. A template-based model generation is not a new idea, but our framework can generate multiple models having different number of pins from a single template. 

## Quick start
Running model validation and generation needs Python packages. As for the package installation, please visit the project homepage (http://vlsiweb.stanford.edu/projects/digitalanalog/).

For a quick start, read and follow the instuction in the GET_STARTED file.

Please read LICENSE file before starting to use.
