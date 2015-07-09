========
Examples
========

L2 Same Domain
--------------

This scenario tests the bandwidth between pairs of instances in the same virtual network (L2 domain).
Each instance is deployed on own compute node. The test increases the load from 1 pair until all
available instances are used.

.. image:: images/topology_l2.png

How To Run
^^^^^^^^^^
.. code::

    shaker --server-endpoint <host:port> --scenario <full_l2.yaml> --report <full_l2.html>

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/networking/full_l2.yaml


L3 East-West
------------

This scenario tests the bandwidth between pairs of instances deployed in different virtual networks
plugged into the same router. Each instance is deployed on its own compute node. The test increases the load
from 1 pair pair until all available instances are used.

.. image:: images/topology_l3_east_west.png

How To Run
^^^^^^^^^^
.. code::

    shaker --server-endpoint <host:port> --scenario <full_l3_east_west.yaml> --report <full_l3_east_west.html>

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/networking/full_l3_east_west.yaml



L3 North-South
--------------

This scenario tests the bandwidth between pairs of instances deployed in different virtual networks. Instances
with master agents are located in one network, instances with slave agents are reached via their floating IPs.
Each instance is deployed on its own compute node. The test increases the load from 1 pair pair until
all available instances are used.

.. image:: images/topology_l3_north_south.png

How To Run
^^^^^^^^^^
.. code::

    shaker --server-endpoint <host:port> --scenario <full_l3_north_south.yaml> --report <full_l3_north_south.html>

Scenario
^^^^^^^^

.. literalinclude:: ../../shaker/scenarios/networking/full_l3_north_south.yaml
