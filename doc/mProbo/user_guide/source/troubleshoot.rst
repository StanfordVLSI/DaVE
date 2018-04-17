***************
Troubleshooting
***************

Ubuntu
======

1. On Ubuntu, after loading the tools environment, you might have the following error: ::

    ImportError: No module named _sysconfigdata_nd; unrecognized arguments
	
This is a bug in the Ubuntu package and does not hurt the functionality of the software.
But, if you'd like to do, this bug can be resolved by creating a link as follows. :: 

    $ sudo ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/
