============
Architecture
============

Shaker tool consists of server and agent modules. The server is executed by ``shaker`` command
and is responsible for deployment of instances, execution of tests as specified in the scenario,
for results processing and report generation. The agent is light-weight and polls tasks from
the server and replies with the results. Agents have connectivity to the server, but the server does not
(so it is easy to keep agents behind NAT).
