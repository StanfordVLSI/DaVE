.. _installation:

************
Installation
************

This *mProbo* tool is provided as a self-extractable file, but it relies on Python language and its built-in and 3rd-party libraries. Therefore, the installation is two-step processes: Python and *mProbo* installation. For Python-related libraries, we strongly suggest to install them using `ANACONDA <https://www.continuum.io/>`_ to avoid any hassle. 


Set up Anaconda Environment
===========================

After installing Anaconda, installing all Python dependencies can be simply done by install the provided package information as follows.

.. include:: _static/env.yaml
  :literal:

One can download the above content as a file (:download:`env.yaml <_static/env.yaml>`) from which `ANACONDA <https://www.continuum.io/>`_ create an environment for *mProbo* by running the command below. ::

  $ conda env create -f env.yaml

Note that the above example is supposed to run under Python 2.7, and thus it is necessary change the content appropriately if other Python version is used. 

Tool Installation
=================

An installation file is named in a format, ``install_mProbo_YYYY-MM.sh``, where *YYYY-MM* represents the software release year and month.
After getting an installation file, the tool can be installed by running the file as follows. ::

  $ ./install_mProbo_YYYY-MM.sh

Depending on a machine on which the tool is being installed, it might need to make the installation file executable like this. ::

  $ chmod +x install_mProbo_YYYY-MM.sh

When running the installation script, it will ask where Anaconda environment is located and where you want to install *mProbo*. When finishing the installation, the script will create a sample environment setup file (``setup.cshrc`` for C-shell, ``setup.sh`` for Bash).

Supported Platform
==================

So far, this tool is tested on the following platforms

  - CentOS 6.5
  - CentOS 7
  - Ubuntu 14.10
