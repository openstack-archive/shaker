Shaker
======

**The distributed data-plane testing tool built for OpenStack.**

Shaker wraps around popular system network testing tools like
`iperf <https://iperf.fr/>`_, `iperf3 <https://iperf.fr/>`_
and netperf (with help of `flent <https://flent.org/>`_).
Shaker is able to deploy OpenStack instances and networks in different
topologies. Shaker scenario specifies the deployment and list of tests
to execute. Additionally tests may be tuned dynamically in command-line.

Features
--------
* User-defined topology via Heat templates
* Simultaneously test execution on multiple instances
* Interactive report with stats and charts
* Built-in SLA verification

Deployment Requirements
-----------------------
* Shaker server routable from OpenStack cloud
* Admin-user access to OpenStack API is preferable

Run in Python Environment
-------------------------

.. code-block:: bash

   $ pip install pyshaker
   $ . openrc
   $ shaker-image-builder
   $ shaker --server-endpoint <host:port> --scenario <scenario> --report <report.html>``

where:
    * ``host`` and ``port`` - host and port of machine where Shaker is deployed
    * ``scenario`` - the scenario to execute, e.g. `openstack/perf_l2` (
      `catalog <http://pyshaker.readthedocs.io/en/latest/catalog.html>`_)
    * ``<report.html>`` - file to store the final report

Full list of parameters is available in `documentation <http://pyshaker.readthedocs.io/en/latest/tools.html#shaker>`_.


Shaker in Container
-------------------

Shaker is available as container at Docker Hub at
`shakhat/shaker <https://hub.docker.com/r/shakhat/shaker/>`_

.. code-block:: bash

    $ docker run -p <port>:<port> -v <artifacts-dir>:/artifacts shakhat/shaker --scenario <scenario> --server-endpoint <host:port>
      --os-auth-url <os-auth-url> --os-username <os-username> --os-password <os-password> --os-project-name <os-project-name>

where:
 * ``host`` and ``port`` - host and port on machine where Shaker is deployed
 * ``artifacts-dir`` - where to store report and raw result
 * ``scenario`` - the scenario to execute, e.g. `openstack/perf_l2` (
   `catalog <http://pyshaker.readthedocs.io/en/latest/catalog.html>`_)
 * ``os-XXX`` - OpenStack cloud credentials


Links
-----
* PyPi - https://pypi.python.org/pypi/pyshaker/
* Docker - https://hub.docker.com/r/shakhat/shaker/
* Docs - http://pyshaker.readthedocs.io/
* Bugtracker - https://launchpad.net/shaker/
