Shaker
======

Shake VMs with our sheer-class tests!

Installation
------------

The tool consists of a single server running on master node and set of dynamically
provisioned agents. In order to run the server needs to know OpenStack parameters
(credentials, auth_url), they can be set via environment (e.g. by sourcing openrc file)
or via parameters.

To install:
 1. ``git clone git://git.openstack.org/stackforge/shaker``
 2. ``python setup.py install`` - installs the tool and all its python dependencies
 3. ``shaker-image-builder`` - builds image for agent VMs inside OpenStack

Note: image builder is able to create Nova flavor optimized for the image and this requires
admin user privileges. However if the flavor is already exists then it can be provided via
``flavor-name`` config parameter and the tool executed from an ordinary user.

How to run
----------
 1. ``shaker --server-endpoint <host>:<port> --scenario <scenario-file> --report <report-file>``

During the run the tool deploys topology, spawns instances, distributes
tasks among instances and generates report in HTML format.

Links
-----
 * Launchpad - https://launchpad.net/shaker/
 * Docs - http://shaker-docs.readthedocs.org/
 * PyPi - https://pypi.python.org/pypi/pyshaker/
