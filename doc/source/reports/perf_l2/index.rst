.. _openstack_l2_performance:

OpenStack L2 Performance
************************

This scenario launches 1 pair of VMs in the same private network on different
compute nodes.

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      - compute_nodes: 2
      template: l2.hot
    description: This scenario launches 1 pair of VMs in the same private network on different
      compute nodes.
    execution:
      tests:
      - class: flent
        method: ping
        sla:
        - '[type == ''agent''] >> (stats.ping_icmp.avg < 0.5)'
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/perf_l2.yaml
    title: OpenStack L2 Performance

Ping
====

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: ping
    sla:
    - '[type == ''agent''] >> (stats.ping_icmp.avg < 0.5)'
    time: 10
    title: Ping

.. image:: 1586aa2e-863f-4469-a613-278bcfac8cb2.*

**Stats**:

.. code-block:: yaml

    ping_icmp:
      max: 4.236238930666339
      avg: 1.0783260741090341
      min: 0.4065897760580819
      unit: ms

**SLA**:

==========================  ===========  =================  ======
Expression                  Concurrency  Node               Result
==========================  ===========  =================  ======
stats.ping_icmp.avg < 0.5             1  node-9.domain.tld  FAIL
==========================  ===========  =================  ======

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

.. image:: 780d525c-da2d-44d4-aa93-3a73a57714cf.*

**Stats**:

.. code-block:: yaml

    bandwidth:
      max: 7492.275238037109
      avg: 7015.98030573527
      min: 5919.618606567383
      unit: Mbit/s
    retransmits:
      max: 1
      avg: 1.0
      min: 1
      unit: ''

**SLA**:

===========================  ===========  =================  ======
Expression                   Concurrency  Node               Result
===========================  ===========  =================  ======
stats.bandwidth.avg > 5000             1  node-9.domain.tld  OK
stats.retransmits.max < 10             1  node-9.domain.tld  OK
===========================  ===========  =================  ======

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

.. image:: b8de3714-e7f0-4109-8a3c-bfb3071c4f2d.*

**Stats**:

.. code-block:: yaml

    packets:
      max: 138160
      avg: 133338.5
      min: 124560
      unit: pps

**SLA**:

===========================  ===========  =================  ======
Expression                   Concurrency  Node               Result
===========================  ===========  =================  ======
stats.packets.avg > 100000             1  node-9.domain.tld  OK
===========================  ===========  =================  ======

