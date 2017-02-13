.. _spot_scenarios:

==============
Spot Scenarios
==============

Spot scenarios are executed between the local machine (where shaker runs) and
the remote. Local machine must have all necessary tools installed, e.g. the
following scenarios require iperf3_ and flent_ utilities.

TCP
---

This scenario tests TCP bandwidth to the destination host. By default it sends traffic to one
of public iperf3 servers. This can be overridden via parameter ``--matrix "{host:<host>}"``.
The scenario requires iperf3_ to be installed locally.

How To Run
^^^^^^^^^^

1. Run the scenario with defaults and generate interactive report into file ``report.html``:

  .. code::

      shaker-spot --scenario spot/tcp --report report.html

2. Run the scenario with overridden target host (10.0.0.2) and store raw result:

  .. code::

      shaker-spot --scenario spot/tcp --matrix "{host:10.0.0.2}" --output report.json

3. Run the scenario with overridden target host (10.0.0.2) and store SLA verification results in `subunit <https://launchpad.net/subunit>`_ stream file:

  .. code::

      shaker-spot --scenario spot/tcp --matrix "{host:10.0.0.2}" --subunit report.subunit

4. Run the scenario against the list of target hosts and store report:

  .. code::

      shaker-spot --scenario spot/tcp --matrix "{host:[10.0.0.2, 10.0.0.3]}" --output report.html

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/spot/tcp.yaml


UDP
---

This scenario tests UDP packets per second to the destination host. By default it sends traffic to one
of public iperf3 servers. This can be overridden via parameter ``--matrix "{host:<host>}"``.
The scenario requires iperf3_ to be installed locally.

How To Run
^^^^^^^^^^

.. code::

  shaker-spot --scenario spot/udp --report report.html

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/spot/udp.yaml


Ping
----

This scenario tests ICMP ping between the local machine and the remote. By default pings are
sent to public 8.8.8.8 address. The remote address can be overridden via parameter
``--matrix "{host: <host>}"``. The scenario requires flent_ to be installed locally.

How To Run
^^^^^^^^^^

.. code::

    shaker-spot --scenario spot/ping --report report.html

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/spot/ping.yaml



.. references:

.. _iperf3: https://iperf.fr/
.. _flent: https://flent.org/
