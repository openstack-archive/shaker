Shaker
======

Distributed data-plane testing tool for OpenStack.

Features
--------

1. Measure the bandwidth between pair of instances in OpenStack.
2. Configurable topology with help of Heat.
3. Simultaneously execution on all available compute nodes.
4. Reports in HTML format with stats and charts
5. Easily extensible to use new tools or other parameters.
6. Scenarios for L2 and L3 testing are included.

Installation
------------

Requirements:

    * OpenStack cloud with admin user (``openrc`` file)
    * Machine routable from instances (instances should have access to it)

Setup:
 1. ``pip install pyshaker`` - installs the tool and all its python dependencies
 2. ``shaker-image-builder`` - builds image for agent VMs inside OpenStack


How to run
----------

 1. ``shaker --server-endpoint <host>:<port> --scenario <scenario-file> --report <report-file>``

During the run the tool deploys topology, spawns instances, distributes
tasks among instances and generates report in HTML format.

Links
-----
 * Launchpad - https://launchpad.net/shaker/
 * Docs - http://pyshaker.readthedocs.org/
 * PyPi - https://pypi.python.org/pypi/pyshaker/
