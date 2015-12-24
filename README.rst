Shaker
======

**The distributed data-plane testing tool built for OpenStack.**

Shaker wraps around popular system network testing tools like
`iperf <https://iperf.fr/>`_, `iperf3 <https://iperf.fr/>`_
and netperf (with help of `flent <https://flent.org/>`_).
Shaker is able to deploy OpenStack instances and networks in different
topologies. Shaker scenario specifies the deployment and list of tests
to execute. Additionally tests may be tuned dynamically in command-line.

Features:

    * User-defined topology via Heat templates
    * Simultaneously test execution on multiple instances
    * Pluggable tools
    * Interactive report with stats and charts
    * Built-in SLA verification

Requirements:

    * Shaker server routable from OpenStack cloud
    * Admin-user access to OpenStack API

Setup:

 1. ``pip install pyshaker`` - installs the tool and all its python dependencies
 2. ``shaker-image-builder`` - builds shaker image and stores it in Glance


Run:

 ``shaker --server-endpoint <host:port> --scenario <scenario.yaml> --report <report.html>``

 where:
    * ``<host:port>`` - address of machine where Shaker is deployed and any free port
    * ``<scenario.yaml>`` - the scenario to execute; L2, L3 east-west and L3 north-south already included
    * ``<report.html>`` - file to store the report


Links:
 * PyPi - https://pypi.python.org/pypi/pyshaker/
 * Docs - http://pyshaker.readthedocs.org/
 * Bugtracker - https://launchpad.net/shaker/
