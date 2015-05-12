========
Examples
========

L2 Same Domain
--------------

This scenario tests the bandwidth between pairs of instances in the same virtual network (L2 domain).
Each instance is deployed on own compute node. The test increases the load from 1 pair until all
available instances are used.

How To Run
^^^^^^^^^^
.. code::

    shaker --server-endpoint <host:port> --scenario <full_l2.yaml> --report <full_l2.html>

Scenario
^^^^^^^^

.. literalinclude:: ../../scenarios/networking/full_l2.yaml


L3 East-West
------------

.. literalinclude:: ../../scenarios/networking/full_l3_east_west.yaml


L3 North-South
--------------

.. literalinclude:: ../../scenarios/networking/full_l3_north_south.yaml
