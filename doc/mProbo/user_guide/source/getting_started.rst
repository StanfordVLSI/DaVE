***************
Getting Started
***************

After setting up the tool environment, you are able to run the checker tool.

Preparing Configuration Files
=============================
To run the tool, a user should provide both a test configuration file and a simulator configuration file. These two files are plain text files which can be created/edited using any text editor such as ``vi``, ``gedit``, and etc., or using our graphical user interface application. The default file name of the test and simulator cofigurations are ``test.cfg`` and ``sim.cfg``, respectively. See :ref:`testconfig` and :ref:`simconfig` on how to write these configuration files.

Running Tool
============

You can invoke the checker tool by typing "``mProbo``" in a shell, and "``mProbo -h``" shows its usage like this. 

.. include:: _static/mProbo_help.scr
  :literal:

Tool Options
------------
The table below explains the options available in ``mProbo``.

+-------------+-----------------+---------------+-----------------------------------------------------------------+
| Option      | Shortcut option | Default value | Description                                                     |
+=============+=================+===============+=================================================================+
| --test      | -t              | test.cfg      | Test configuration file name                                    |
+-------------+-----------------+---------------+-----------------------------------------------------------------+
| --sim       | -s              | sim.cfg       | Simulator configuration file name                               |
+-------------+-----------------+---------------+-----------------------------------------------------------------+
| --rpt       | -r              | report.html   | Checker result file name in HTML                                |
+-------------+-----------------+---------------+-----------------------------------------------------------------+
| --process   | -p              | 1             | Number of processes for multi-processing support                |
+-------------+-----------------+---------------+-----------------------------------------------------------------+
| --use-cache | -c              | N/A           | Use simulation data in ``.mProbo`` directory from previous runs |
+-------------+-----------------+---------------+-----------------------------------------------------------------+
| --gui       | -g              | N/A           | Invoke GUI editor of test/simulator configuration files         |
+-------------+-----------------+---------------+-----------------------------------------------------------------+

Reading Checking Results
========================

The checking results are stored in *HTML* format, so you can open the report using any web browser such as Firefox, Chrome, and so on. The default report file name is ``report.html``.

