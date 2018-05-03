Getting Started
===============

After installing "DaVE" and Python libraries, first read LICENSE TERMS in the installation directory. If you agree with the license terms, you can start playing with the tool.

Tweaking sample setup file
--------------------------
Edit either "setup.cshrc" for C-shell or "setup.sh" for BASH for proper tool setup. Please open the files and edit the values of "DAVE_INST_DIR" and "PYTHONHOME" variables properly.

Loading Tool Environment
------------------------
We provide sample scripts ("setup.cshrc" for C-Shell, "setup.sh" for BASH) in the installation directory. Thus the first step is to source the environment. For example, one can source a C-Shell setup script like this.

$ source setup.cshrc

The next step is to load simulator environments. Since loading the simulator is different for entities, one needs to load the simulator environment by oneself. Note that one only needs Synopsys' VCS and/or Cadence' Incisive for analog model simulations, but "Dave" only supports Cadence's Incisive for AMS simulations (for AMS equivalence checking).

Quick Start
-----------
After loading the "DaVE" environment and your simulator environment, one can test whethere the setup is done properly by running a few examples. 

For analog model simulations, follow the steps below.

$ cd mLingua/examples/spf/sim

$ make

If "DaVE" and Python libraries are installed correctly, you will see a post-script file ("spf_step_response.eps") which can be opened using Gostscript (command name is "gs").

For model equivalence checking, follow the steps below.

$ cd mProbo/examples/amux

$ mProbo -p 1

If the setup is done correctly, you will see "mProbo" tool is running and it will generate "report.html" file after finishing the checking.

Model Modeling examples
-----------------------
There are more model examples under mLingua/examples
