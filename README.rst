Shaker
======

Distributed data-plane testing tool for OpenStack.

Features
--------

1. Measure the bandwidth between two instances in OpenStack.
2. Easily configurable deployment with help of Heat
3. Load testing of the whole cloud
4. Reports in HTML format with stats and charts
5. Easily extensible to new tools

Installation
------------

The tool consists of a single server running on master node and set of dynamically
provisioned agents. In order to run the server needs to know OpenStack parameters
(credentials, auth_url), they can be set via environment (e.g. by sourcing openrc file)
or via parameters.

To install:
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
