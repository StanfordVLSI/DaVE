.. _envsetup:

******************
Environment Setup
******************
After installing *mProbo*, it is necessary to properly set up the tool enviroment. By default, the *mProbo* installation script will create a sample environment setup file (:download:`setup.cshrc <_static/setup.cshrc>` for C-shell, :download:`setup.sh <_static/setup.sh>` for Bash) under your installation directory. However, it does not include the environment setup for simulators such as Synopsys' VCS, Cadence' NCSIM, etc., which is supposed to be added by customers. In most cases, simply sourcing the aforementioned setup file should be fine for running *mProbo*. 

Environment Variables
=====================

The table below lists all the environment variables reserved for *mProbo*. The variable names are case sensitive.

+-------------------+--------------------------------------------------------------------------------------------------+
| Name              | Description                                                                                      |
+===================+==================================================================================================+
| DAVE_INST_DIR     | Installation directory of *DaVE* includes (*mProbo*, *mLinuga*, *mGenero*)                       |
+-------------------+--------------------------------------------------------------------------------------------------+
| DAVE_SAMPLES      | Sample directory. This is typically `$DAVE_INST_DIR/samples`                                     |
+-------------------+--------------------------------------------------------------------------------------------------+
| mPROBO_DIR        | Installation directory of *mPROBO* under ``DAVE_INST_DIR``                                       |
+-------------------+--------------------------------------------------------------------------------------------------+
| mPROBO_DEMO_DIR   | Example directory of *mPROBO*                                                                    |
+-------------------+--------------------------------------------------------------------------------------------------+
| PYTHONHOME        | Python home directory. See the sample setup script how it is configured with Anaconda.           |
+-------------------+--------------------------------------------------------------------------------------------------+
| LD_LIBRARY_PATH   | Dynamically linked library path. See the sample setup script how it is configured with Anaconda. |
+-------------------+--------------------------------------------------------------------------------------------------+
| mLINGUA_DIR       | Installation directory of *mLINGUA* under ``DAVE_INST_DIR``                                      |
+-------------------+--------------------------------------------------------------------------------------------------+
| mLINGUA_DEMO_DIR  | Example directory of *mLINGUA*                                                                   |
+-------------------+--------------------------------------------------------------------------------------------------+
| mLINGUA_SIMULATOR | Default SystemVerilog simulator for *mLINGUA*                                                    |
+-------------------+--------------------------------------------------------------------------------------------------+
| mGENERO_DIR       | Installation directory of *mGENERO* under ``DAVE_INST_DIR``                                      |
+-------------------+--------------------------------------------------------------------------------------------------+
| mGENERO_DEMO_DIR  | Example directory of *mGENERO*                                                                   |
+-------------------+--------------------------------------------------------------------------------------------------+

The directory contains the executable files of the tool should be added to your shell path. For example, the following shows a statement in C-shell. ::

  set path = ( ${DAVE_INST_DIR}/bin $path )

Sample Setup Script
===================

A sample setup file, ``setup.cshrc`` and ``setup.sh``, are provided in the installation directory.

.. include:: _static/setup.cshrc
  :literal:

.. include:: _static/setup.sh
  :literal:

