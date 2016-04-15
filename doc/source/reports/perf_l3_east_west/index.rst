.. _openstack_l3_east_west_performance:

OpenStack L3 East-West Performance
**********************************

This scenario launches 1 pair of VMs in different networks connected to one
router (L3 east-west). VMs are hosted on different compute nodes

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      - compute_nodes: 2
      template: l3_east_west.hot
    description: This scenario launches 1 pair of VMs in different networks connected
      to one router (L3 east-west). VMs are hosted on different compute nodes
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/perf_l3_east_west.yaml
    title: OpenStack L3 East-West Performance

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

.. image:: 0549ebdf-5903-4592-ab06-5c12b10fc625.*

**Stats**:

.. code-block:: yaml

    ping_icmp:
      max: 3.880741082830054
      avg: 1.23610103398376
      min: 0.7130612739715825
      unit: ms

**SLA**:

==========================  ===========  ==================  ======
Expression                  Concurrency  Node                Result
==========================  ===========  ==================  ======
stats.ping_icmp.avg < 2.0             1  node-19.domain.tld  OK
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

.. image:: 489cd75f-c740-477f-9e03-9e0adf043ccf.*

**Stats**:

.. code-block:: yaml

    bandwidth:
      max: 5531.473159790039
      avg: 4966.737230682373
      min: 3640.0222778320312
      unit: Mbit/s
    retransmits:
      max: 4
      avg: 4.0
      min: 4
      unit: ''

**SLA**:

===========================  ===========  ==================  ======
Expression                   Concurrency  Node                Result
===========================  ===========  ==================  ======
stats.bandwidth.avg > 5000             1  node-19.domain.tld  FAIL
stats.retransmits.max < 10             1  node-19.domain.tld  OK
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

.. image:: c27bc4a9-b379-4f18-bcff-ff24e1f35ead.*

**Stats**:

.. code-block:: yaml

    packets:
      max: 141310
      avg: 137370.33333333334
      min: 135180
      unit: pps

**SLA**:

===========================  ===========  ==================  ======
Expression                   Concurrency  Node                Result
===========================  ===========  ==================  ======
stats.packets.avg > 100000             1  node-19.domain.tld  OK
===========================  ===========  ==================  ======

