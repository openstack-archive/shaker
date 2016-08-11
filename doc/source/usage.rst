=====
Usage
=====

Configuration
-------------

For OpenStack scenarios the connection is configured using standard
``openrc`` file (refer to
http://docs.openstack.org/cli-reference/common/cli_set_environment_variables_using_openstack_rc.html
on how to retrieve it).
The config can be passed to Shaker rather by sourcing into system env ``source openrc``
or via set of CLI parameters ``--os-project-name``, ``--os-username``, ``--os-password``,
``--os-auth-url`` and ``--os-region-name``.
Connection to SSL endpoints is configured by parameters ``--os-cacert`` and ``--os-insecure``
(to disable certificate verification). Configuration can also be specified in
config file, refer to :ref:`config`. Config file name can be passed by parameter ``--config-file``.

.. note::
    Shaker is better run under user with admin privileges. However, it's possible
    to run under ordinary user too - refer to :ref:`non_admin_mode`


Common Parameters
-----------------

The following parameters are applicable for both OpenStack mode (`shaker`) and spot mode (`shaker-spot`).

1. Run the scenario with defaults and generate interactive report into file `report.html`:

  .. code::

      shaker --scenario <scenario> --report report.html

2. Run the scenario and store raw result:

  .. code::

      shaker --scenario <scenario> --output output.json

3. Run the scenario and store SLA verification results in `subunit <https://launchpad.net/subunit>`_ stream file:

  .. code::

      shaker --scenario <scenario> --subunit report.subunit

4. Generate report from the raw data:

  .. code::

      shaker-report --input output.json --output report.html


Scenario Explained
------------------

Shaker scenario is file in YAML format. It describes how agents are deployed
(at OpenStack instances or statically) and sequence of tests to execute. When agents
are deployed at OpenStack instances a reference to Heat template is provided.

.. code::

    description:
      This scenario launches pairs of VMs in the same private network. Every VM is
      hosted on a separate compute node.

    deployment:
      template: l2.hot
      accommodation: [pair, single_room]

    execution:
      progression: quadratic
      tests:
      -
        title: Iperf TCP
        class: iperf_graph
        time: 60

Deployment
^^^^^^^^^^

By default Shaker spawns  instances on every available compute node. The distribution
of instances is configured by parameter ``accommodation``. There are several instructions
that allow control the scheduling precisely:

    * ``pair`` - instances are grouped in pairs, meaning that one can be used as source of traffic and the other as a consumer (needed for networking tests)
    * ``single_room`` - 1 instance per compute node
    * ``double_room`` - 2 instances per compute node
    * ``density: N`` - the multiplier for number of instances per compute node
    * ``compute_nodes: N`` - how many compute nodes should be used (by default Shaker use all of them)
    * ``zones: [Z1, Z2]`` - list of Nova availability zones to use

Examples:

.. image:: images/accommodation_single_room.*

.. image:: images/accommodation_double_room.*

As result of deployment the set of agents is produced. For networking testing this set contains
agents in ``master`` and ``slave`` roles. Master agents are controlled by ``shaker`` tool and execute commands.
Slaves are used as back-ends and do not receive any commands directly.

Execution
^^^^^^^^^

The execution part of scenario contains a list of tests that are executed one by one. By default Shaker runs the test
simultaneously on all available agents. The level of concurrency can be controlled by option ``progression``. There are
3 values available:

    * no value specified - all agents are involved;
    * ``linear`` - the execution starts with 1 agent and increases by 1 until all agents are involved;
    * ``quadratic`` - the execution starts with 1 agent (or 1 pair) and doubles until all agents are involved.

Tests are executed in order of definition. The exact action is defined by option ``class``, additional attributes are provided
by respective parameters. The following classes are available:

    * ``iperf3`` - runs ``iperf3`` tool and shows chart and statistics
    * ``flent`` - runs ``flent`` (http://flent.org) and shows chart and statistics
    * ``iperf`` - runs ``iperf`` tool and shows plain output
    * ``netperf`` - runs ``netpers`` tool and shows plain output
    * ``shell`` - runs any shell command or process and shows plain output
    * ``iperf_graph`` - runs ``iperf`` tool and shows chart and statistics (deprecated)

Test classes
^^^^^^^^^^^^

Tools are configured via key-value attributes in test definition. For all networking tools Shaker offers unified parameters, that are translated
automatically.

iperf3, iperf, iperf_graph:
~~~~~~~~~~~~~~~~~~~~~~~~~~~
    * ``time`` - time in seconds to transmit for, defaults to `60`
    * ``udp`` - use UDP instead of TCP, defaults to `TCP`
    * ``interval`` - seconds between periodic bandwidth reports, defaults to `1 s`
    * ``bandwidth`` - for UDP, bandwidth to send at in bits/sec, defaults to `1 Mbit/s`
    * ``threads`` - number of parallel client threads to run
    * ``host`` - the address of destination host to run the tool against, defaults to IP address of slave agent
    * ``datagram_size`` - the size of UDP datagrams
    * ``mss`` - set TCP maximum segment size

flent:
~~~~~~
    * ``time`` - time in seconds to transmit for, defaults to `60`
    * ``interval`` - seconds between periodic bandwidth reports, defaults to `1`
    * ``method`` - which flent scenario to use, see https://github.com/tohojo/flent/tree/master/flent/tests for the whole list, defaults to `tcp_download`
    * ``host`` - the address of destination host to run the tool against, defaults to IP address of slave agent


netperf:
~~~~~~~~
    * ``time`` - time in seconds to transmit for, defaults to `60`
    * ``method`` - one of built-in test names, see http://linux.die.net/man/1/netperf for the whole list, defaults to `TCP_STREAM`
    * ``host`` - the address of destination host to run the tool against, defaults to IP address of slave agent

shell:
~~~~~~
    * ``program`` - run single program
    * ``script`` - run bash script


SLA validation
^^^^^^^^^^^^^^

Test case can contain SLA rules that are calculated upon test completion.
Every rule has 2 parts: record selector and condition. The record selector allows
to filter only subset of all records, e.g. of type `agent` to filter records produced
by a single agent. The condition applies to particular statistics.

SLA examples:
 * ``[type == 'agent'] >> (stats.bandwidth.min > 1000)`` - require min bandwidth on every agent be at least 1000 Mbit
 * ``[type == 'agent'] >> (stderr == '')`` - require stderr to be empty

Results of SLA validation can be obtained by generating output in subunit format.
To do this a file name should be provided via `--subunit` parameter.
