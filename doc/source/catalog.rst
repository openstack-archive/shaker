.. _catalog:

Scenario Catalog
================

Scenarios
---------

.. _scenario_openstack_instances_metadata_query:

OpenStack instances metadata query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches ten instances on a single compute node and
asks instances to retrieve the metadata. The scenario is used to load metadata
processes.

To use this scenario specify parameter ``--scenario misc/instance_metadata``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/misc/instance_metadata.yaml

.. _scenario_static_agents:

Static agents
^^^^^^^^^^^^^
In this scenario Shaker runs tests on pre-deployed static agents. The scenario
can be used for Shaker integration testing.

To use this scenario specify parameter ``--scenario misc/static_agent``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/misc/static_agent.yaml

.. _scenario_paired_static_agents:

Paired static agents
^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker runs tests on pre-deployed pair of static agents. The
scenario can be used for Shaker integration testing.

To use this scenario specify parameter ``--scenario misc/static_agents_pair``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/misc/static_agents_pair.yaml

.. _scenario_openstack_l2_cross_az:

OpenStack L2 Cross-AZ
^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances in the same tenant network.
Every instance is hosted on a separate compute node, all available compute
nodes are utilized. The master and slave instances are in different
availability zones. The scenario is used to test throughput between `nova` and
`vcenter` zones. The traffic goes within the tenant network (L2 domain).

To use this scenario specify parameter ``--scenario openstack/cross_az/full_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/full_l2.yaml

.. _scenario_openstack_l3_east_west_cross_az:

OpenStack L3 East-West Cross-AZ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances, each instance on its own
compute node. All available compute nodes are utilized. Instances are connected
to one of 2 tenant networks, which plugged into single router. The traffic goes
from one network to the other (L3 east-west). The master and slave instances
are in different availability zones. The scenario is used to test throughput
between `nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/full_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/full_l3_east_west.yaml

.. _scenario_openstack_l3_north_south_cross_az:

OpenStack L3 North-South Cross-AZ
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances on different compute nodes.
All available compute nodes are utilized. Instances are in different networks
connected to different routers, master accesses slave by floating ip. The
traffic goes from one network via external network to the other network. The
master and slave instances are in different availability zones. The scenario is
used to test throughput between `nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/full_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/full_l3_north_south.yaml

.. _scenario_openstack_l2_cross_az_performance:

OpenStack L2 Cross-AZ Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances in the same tenant
network. Each instance is hosted on a separate compute node. The master and
slave instances are in different availability zones. The scenario is used to
test throughput between `nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/perf_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/perf_l2.yaml

.. _scenario_openstack_l3_east_west_cross_az_performance:

OpenStack L3 East-West Cross-AZ Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances, each instance on its own
compute node. Instances are connected to one of 2 tenant networks, which
plugged into single router. The traffic goes from one network to the other (L3
east-west). The master and slave instances are in different availability zones.
The scenario is used to test throughput between `nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/perf_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/perf_l3_east_west.yaml

.. _scenario_openstack_l3_north_south_cross_az_performance:

OpenStack L3 North-South Cross-AZ Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances on different compute
nodes. Instances are in different networks connected to different routers,
master accesses slave by floating ip. The traffic goes from one network via
external network to the other network. The master and slave instances are in
different availability zones. The scenario is used to test throughput between
`nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/perf_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/perf_l3_north_south.yaml

.. _scenario_openstack_l2_cross_az_udp:

OpenStack L2 Cross-AZ UDP
^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances in the same tenant network.
Every instance is hosted on a separate compute node. The load is generated by
UDP traffic. The master and slave instances are in different availability
zones. The scenario is used to test throughput between `nova` and `vcenter`
zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/udp_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/udp_l2.yaml

.. _scenario_openstack_l2_cross_az_udp_jumbo:

OpenStack L2 Cross-AZ UDP Jumbo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances in the same tenant network.
Every instance is hosted on a separate compute node. The load is generated by
UDP traffic and jumbo packets. The master and slave instances are in different
availability zones. The scenario is used to test throughput between `nova` and
`vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/udp_l2_mss8950``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/udp_l2_mss8950.yaml

.. _scenario_openstack_l3_east_west_cross_az_udp:

OpenStack L3 East-West Cross-AZ UDP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances, each instance on its own
compute node. Instances are connected to one of 2 tenant networks, which
plugged into single router. The traffic goes from one network to the other (L3
east-west). The load is generated by UDP traffic. The master and slave
instances are in different availability zones. The scenario is used to test
throughput between `nova` and `vcenter` zones.

To use this scenario specify parameter ``--scenario openstack/cross_az/udp_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/udp_l3_east_west.yaml

.. _scenario_openstack_l2_dense:

OpenStack L2 Dense
^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches several pairs of instances on a single compute
node. Instances are plugged into the same tenant network. The traffic goes
within the tenant network (L2 domain).

To use this scenario specify parameter ``--scenario openstack/dense_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/dense_l2.yaml

.. _scenario_openstack_l3_east_west_dense:

OpenStack L3 East-West Dense
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances on the same compute node.
Instances are connected to different tenant networks connected to one router.
The traffic goes from one network to the other (L3 east-west).

To use this scenario specify parameter ``--scenario openstack/dense_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/dense_l3_east_west.yaml

.. _scenario_openstack_l3_north_south_dense:

OpenStack L3 North-South Dense
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances on the same compute node.
Instances are connected to different tenant networks, each connected to own
router. Instances in one of networks have floating IPs. The traffic goes from
one network via external network to the other network.

To use this scenario specify parameter ``--scenario openstack/dense_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/dense_l3_north_south.yaml

.. _scenario_openstack_l3_north_south_dense_to_external_target:

OpenStack L3 North-South Dense to external target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instances on one compute node in a tenant
network connected to external network. The traffic is sent to and from external
host. The host name needs to be provided as command-line parameter, e.g.
``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/dense_l3_north_south_no_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/dense_l3_north_south_no_fip.yaml

.. _scenario_openstack_l3_north_south_dense_to_external_target_with_floating_ip:

OpenStack L3 North-South Dense to external target with floating IP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instances on one compute node in a tenant
network connected to external network. All instances have floating IPs. The
traffic is sent to and from external host. The host name needs to be provided
as command-line parameter, e.g. ``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/dense_l3_north_south_with_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/dense_l3_north_south_with_fip.yaml

.. _scenario_openstack_l3_north_south_to_external_target:

OpenStack L3 North-South to external target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instances in a tenant network connected to
external network. Every instance is hosted on dedicated compute node. All
available compute nodes are utilized. The traffic is sent to and from external
host (L3 north-south). The host name needs to be provided as command-line
parameter, e.g. ``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/full_l3_north_south_no_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/full_l3_north_south_no_fip.yaml

.. _scenario_openstack_l3_north_south_to_external_target_with_floating_ip:

OpenStack L3 North-South to external target with floating IP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instances in a tenant network connected to
external network. Every instance is hosted on dedicated compute node. All
available compute nodes are utilized. All instances have floating IPs. The
traffic is sent to and from external host (L3 north-south). The host name needs
to be provided as command-line parameter, e.g. ``--matrix "{host:
172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/full_l3_north_south_with_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/full_l3_north_south_with_fip.yaml

.. _scenario_openstack_l3_north_south_performance_to_external_target:

OpenStack L3 North-South Performance to external target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instance in a tenant network connected to
external network. The traffic is sent to and from external host. By default one
of public iperf3 servers is used, to override this the target host can be
provided as command-line parameter, e.g. ``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/perf_l3_north_south_no_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/perf_l3_north_south_no_fip.yaml

.. _scenario_openstack_l3_north_south_performance_to_external_target_with_floating_ip:

OpenStack L3 North-South performance to external target with floating IP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches instance in a tenant network connected to
external network. The instance has floating IP. The traffic is sent to and from
external host. By default one of public iperf3 servers is used, to override
this the target host can be provided as command-line parameter, e.g. ``--matrix
"{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario openstack/external/perf_l3_north_south_with_fip``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/perf_l3_north_south_with_fip.yaml

.. _scenario_openstack_l2:

OpenStack L2
^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances in the same tenant network.
Every instance is hosted on a separate compute node, all available compute
nodes are utilized. The traffic goes within the tenant network (L2 domain).

To use this scenario specify parameter ``--scenario openstack/full_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/full_l2.yaml

.. _scenario_openstack_l3_east_west:

OpenStack L3 East-West
^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances, each instance on its own
compute node. All available compute nodes are utilized. Instances are connected
to one of 2 tenant networks, which plugged into single router. The traffic goes
from one network to the other (L3 east-west).

To use this scenario specify parameter ``--scenario openstack/full_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/full_l3_east_west.yaml

.. _scenario_openstack_l3_north_south:

OpenStack L3 North-South
^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances on different compute nodes.
All available compute nodes are utilized. Instances are in different networks
connected to different routers, master accesses slave by floating ip. The
traffic goes from one network via external network to the other network.

To use this scenario specify parameter ``--scenario openstack/full_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/full_l3_north_south.yaml

.. _scenario_openstack_l2_performance:

OpenStack L2 Performance
^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances in the same tenant
network. Each instance is hosted on a separate compute node. The traffic goes
within the tenant network (L2 domain).

To use this scenario specify parameter ``--scenario openstack/perf_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/perf_l2.yaml

.. _scenario_openstack_l3_east_west_performance:

OpenStack L3 East-West Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances, each instance on its own
compute node. Instances are connected to one of 2 tenant networks, which
plugged into single router. The traffic goes from one network to the other (L3
east-west).

To use this scenario specify parameter ``--scenario openstack/perf_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/perf_l3_east_west.yaml

.. _scenario_openstack_l3_north_south_performance:

OpenStack L3 North-South Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances on different compute
nodes. Instances are in different networks connected to different routers,
master accesses slave by floating ip. The traffic goes from one network via
external network to the other network.

To use this scenario specify parameter ``--scenario openstack/perf_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/perf_l3_north_south.yaml

.. _scenario_openstack_l2_qos_performance:

OpenStack L2 QoS Performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches 1 pair of instances in the same tenant
network. Each instance is hosted on a separate compute node. The traffic goes
within the tenant network (L2 domain). Neutron QoS feature is used to limit
traffic throughput to 10 Mbit/s.

To use this scenario specify parameter ``--scenario openstack/qos/perf_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/qos/perf_l2.yaml

.. _scenario_openstack_l2_udp:

OpenStack L2 UDP
^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances in the same tenant network.
Every instance is hosted on a separate compute node. The traffic goes within
the tenant network (L2 domain). The load is generated by UDP traffic.

To use this scenario specify parameter ``--scenario openstack/udp_l2``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/udp_l2.yaml

.. _scenario_openstack_l3_east_west_udp:

OpenStack L3 East-West UDP
^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances, each instance on its own
compute node. Instances are connected to one of 2 tenant networks, which
plugged into single router. The traffic goes from one network to the other (L3
east-west). The load is generated by UDP traffic.

To use this scenario specify parameter ``--scenario openstack/udp_l3_east_west``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/udp_l3_east_west.yaml

.. _scenario_openstack_l3_north_south_udp:

OpenStack L3 North-South UDP
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In this scenario Shaker launches pairs of instances on different compute nodes.
Instances are in different networks connected to different routers, master
accesses slave by floating ip. The traffic goes from one network via external
network to the other network. The load is generated by UDP traffic.

To use this scenario specify parameter ``--scenario openstack/udp_l3_north_south``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/udp_l3_north_south.yaml

.. _scenario_ping:

Ping
^^^^
This scenario uses ping to measure the latency between the local host and the
remote. The remote host can be provided via command-line, it defaults to
8.8.8.8. The scenario verifies SLA and expects the latency to be at most 30ms.
The destination host can be overridden by command-line parameter, e.g.
``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario spot/ping``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/spot/ping.yaml

.. _scenario_tcp_bandwidth:

TCP bandwidth
^^^^^^^^^^^^^
This scenario uses iperf3 to measure TCP throughput between local host and
ping.online.net (or against hosts provided via CLI). SLA check is verified and
expects the speed to be at least 90Mbit and at most 20 retransmitts. The
destination host can be overridden by command-line parameter, e.g. ``--matrix
"{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario spot/tcp``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/spot/tcp.yaml

.. _scenario_udp_bandwidth:

UDP bandwidth
^^^^^^^^^^^^^
This scenario uses iperf3 to measure UDP throughput between local host and
ping.online.net (or against hosts provided via CLI). SLA check is verified and
requires at least 10 000 packets per second. The destination host can be
overridden by command-line parameter, e.g. ``--matrix "{host: 172.10.1.2}"``.

To use this scenario specify parameter ``--scenario spot/udp``.
Scenario source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/spot/udp.yaml

Heat Templates
--------------

.. _template_misc_instance_metadata:

misc/instance_metadata
^^^^^^^^^^^^^^^^^^^^^^
Heat template creates a new Neutron network, a router to the external network,
plugs instances into this network and assigns floating ips

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/misc/instance_metadata.hot

.. _template_openstack_cross_az_l2:

openstack/cross_az/l2
^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network, a router to the external
network and plugs instances into this new network. All instances are located in
the same L2 domain.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/l2.hot

.. _template_openstack_cross_az_l3_east_west:

openstack/cross_az/l3_east_west
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a pair of networks plugged into the same router.
Master instances and slave instances are connected into different networks.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/l3_east_west.hot

.. _template_openstack_cross_az_l3_north_south:

openstack/cross_az/l3_north_south
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network plus a north_router to the
external network. The template also assigns floating IP addresses to each
instance so they are routable from the external network.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/cross_az/l3_north_south.hot

.. _template_openstack_external_l3_north_south_no_fip:

openstack/external/l3_north_south_no_fip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network plugged into a router
connected to the external network, and boots an instance in that network.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/l3_north_south_no_fip.hot

.. _template_openstack_external_l3_north_south_with_fip:

openstack/external/l3_north_south_with_fip
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network plugged into a router
connected to the external network, and boots an instance in that network. The
instance has floating IP.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/external/l3_north_south_with_fip.hot

.. _template_openstack_l2:

openstack/l2
^^^^^^^^^^^^
This Heat template creates a new Neutron network, a router to the external
network and plugs instances into this new network. All instances are located in
the same L2 domain.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/l2.hot

.. _template_openstack_l3_east_west:

openstack/l3_east_west
^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a pair of networks plugged into the same router.
Master instances and slave instances are connected into different networks.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/l3_east_west.hot

.. _template_openstack_l3_north_south:

openstack/l3_north_south
^^^^^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network plus a north_router to the
external network. The template also assigns floating IP addresses to each
instance so they are routable from the external network.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/l3_north_south.hot

.. _template_openstack_qos_l2_qos:

openstack/qos/l2_qos
^^^^^^^^^^^^^^^^^^^^
This Heat template creates a new Neutron network, a router to the external
network and plugs instances into this new network. All instances are located in
the same L2 domain.

Template source is available at: https://github.com/openstack/shaker/blob/master/shaker/scenarios/openstack/qos/l2_qos.hot

