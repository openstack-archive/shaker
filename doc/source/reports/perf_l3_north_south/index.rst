.. _openstack_l3_north_south_performance:

OpenStack L3 North-South Performance
************************************

This scenario launches 1 pair of VMs on different compute nodes. VMs are in the
different networks connected via different routers, master accesses slave by
floating ip

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      - compute_nodes: 2
      template: l3_north_south.hot
    description: This scenario launches 1 pair of VMs on different compute nodes. VMs
      are in the different networks connected via different routers, master accesses slave
      by floating ip
    execution:
      tests:
      - class: flent
        method: ping
        sla:
        - '[type == ''agent''] >> (stats.ping_icmp.avg < 2.0)'
        time: 10
        title: Ping
      - class: iperf3
        sla:
        - '[type == ''agent''] >> (stats.bandwidth.avg > 5000)'
        - '[type == ''agent''] >> (stats.retransmits.max < 10)'
        title: TCP
      - bandwidth: 0
        class: iperf3
        datagram_size: 32
        sla:
        - '[type == ''agent''] >> (stats.packets.avg > 100000)'
        title: UDP
        udp: true
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/perf_l3_north_south.yaml
    title: OpenStack L3 North-South Performance

Ping
====

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: ping
    sla:
    - '[type == ''agent''] >> (stats.ping_icmp.avg < 2.0)'
    time: 10
    title: Ping

.. image:: 42af5820-53ae-4dcb-a268-b59c046698a5.*

**Stats**:

.. code-block:: yaml

    ping_icmp:
      max: 3.4270406725254006
      avg: 1.6479111172469332
      min: 0.9622029103967339
      unit: ms

**SLA**:

==========================  ===========  ==================  ======
Expression                  Concurrency  Node                Result
==========================  ===========  ==================  ======
stats.ping_icmp.avg < 2.0             1  node-11.domain.tld  OK
==========================  ===========  ==================  ======

TCP
===

**Test Specification**:

.. code-block:: yaml

    class: iperf3
    interval: 1
    sla:
    - '[type == ''agent''] >> (stats.bandwidth.avg > 5000)'
    - '[type == ''agent''] >> (stats.retransmits.max < 10)'
    title: TCP

.. image:: 44aea6a5-541d-43a0-a331-42fdcada8ac6.*

**Stats**:

.. code-block:: yaml

    bandwidth:
      max: 904.4981002807617
      avg: 868.6801114400228
      min: 508.1815719604492
      unit: Mbit/s
    retransmits:
      max: 470
      avg: 135.0
      min: 1
      unit: ''

**SLA**:

===========================  ===========  ==================  ======
Expression                   Concurrency  Node                Result
===========================  ===========  ==================  ======
stats.bandwidth.avg > 5000             1  node-11.domain.tld  FAIL
stats.retransmits.max < 10             1  node-11.domain.tld  FAIL
===========================  ===========  ==================  ======

UDP
===

**Test Specification**:

.. code-block:: yaml

    bandwidth: 0
    class: iperf3
    datagram_size: 32
    interval: 1
    sla:
    - '[type == ''agent''] >> (stats.packets.avg > 100000)'
    title: UDP
    udp: true

.. image:: 4effd839-3d1a-49ab-a9e0-9ad4f2a1434e.*

**Stats**:

.. code-block:: yaml

    packets:
      max: 140930
      avg: 137099.0
      min: 135620
      unit: pps

**SLA**:

===========================  ===========  ==================  ======
Expression                   Concurrency  Node                Result
===========================  ===========  ==================  ======
stats.packets.avg > 100000             1  node-11.domain.tld  OK
===========================  ===========  ==================  ======

