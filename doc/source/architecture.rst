============
Architecture
============

Shaker tool consists of server and agent modules. The server is executed by ``shaker`` command
and is responsible for deployment of instances, execution of tests as specified in the scenario,
for results processing and report generation. The agent is light-weight and polls tasks from
the server and replies with the results. Agents have connectivity to the server, but the server does not
(so it is easy to keep agents behind NAT).

.. image:: images/architecture.*


Under the Hood
^^^^^^^^^^^^^^

Scenario execution involves the following steps:

    1. User launches shaker with the following minimum set of parameters::

        shaker --server-endpoint <host:port> --scenario <scenario> --report <report>

       where:
          * host:port - address of the machine where Shaker is installed and
            port is some arbitrary free port to bind the server to;
          * scenario - file name of the scenario (yaml file);
          * report - file name where report will be saved.

    2. Shaker verifies connection to OpenStack. The parameters are taken from set of os-* params or from the env (``openrc``).

    3. Based on ``accommodation`` parameter the list of agents is generated.

    4. The topology is deployed with help of Heat. The list of agents is extended with IP addresses and instance names.

    5. Shaker waits for all agents to join. Once all agents are alive it means
       that the quorum exists and everyone ready to execute the tests.

    6. Shaker starts tests one by one in order they are listed in the scenario.
       Test definition is converted into the actual command that will be
       executed by agent. Shaker schedules the command to be started at the same
       time on all agents. For networking testing only agents in ``master`` role
       are involved. Slave agents are used as back-end for corresponding commands
       (i.e. they run iperf in server mode).

    7. Agents send their results to the server. Once all replies are received
       the test execution meant to be finished. If some agent didn't make it in
       dedicated time it is marked as lost.

    8. Once all tests are executed Shaker can output the raw result in JSON format
       (if option ``--output`` is set).

    9. Shaker clears the topology by calling Heat.

    10. Shaker calculates statistics and aggregated charts. If there are any
        SLA statements they are also evaluated, the result can be stored in subunit format
        (if option ``--subunit`` is set).

    11. Shaker generates report in HTML format into file specified by ``--report`` option.
