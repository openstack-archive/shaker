Shaker
======

The distributed data-plane testing tool for OpenStack.

Features
--------

    * User-defined topology via Heat templates
    * Simultaneously test execution on multiple instances
    * Pluggable tools
    * Interactive report with stats and charts

Requirements
------------

    * Shaker server routable from OpenStack cloud
    * Admin-user access to OpenStack API

Setup
-----

 1. ``pip install pyshaker`` - installs the tool and all its python dependencies
 2. ``shaker-image-builder`` - builds shaker image and stores it in Glance


Run
---

 ``shaker --server-endpoint <host:port> --scenario <scenario.yaml> --report <report.html>``

 where:
    * ``<host:port>`` - address of machine where Shaker is deployed and any free port
    * ``<scenario.yaml>`` - the scenario to execute; L2, L3 east-west and L3 north-south already included
    * ``<report.html>`` - file to store the report


Links
-----
 * Launchpad - https://launchpad.net/shaker/
 * Docs - http://pyshaker.readthedocs.org/
 * PyPi - https://pypi.python.org/pypi/pyshaker/
