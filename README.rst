Shaker
======

Shake VMs with our sheer-class tests!

Installation
------------

The tool requires OpenStack clients to be installed and available from the system shell.
OpenStack user must be specified in the environment (e.g. via sourcing openrc file).
During installation the tool uploads Ubuntu cloud image, boots VM, installs all needed packages
into it and creates snapshot with name ``shaker-image``. The VM is launched in Fuel default network
or in the one set by ``NETWORK_NAME`` variable

To install:
 1. Run ``./bin/prepare.sh`` to configure the image inside OpenStack
 2. Run ``python setup.py install`` to install the tool on the master node

Additional dependencies: tests that use netperf requires ``numpy`` and ``matplotlib`` Python modules
to be installed on the master.

How to run
----------
 1. ``shaker --scenario <scenario-file>``
