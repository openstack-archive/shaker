=====
Usage
=====

Configuration
-------------

The connection to OpenStack is configured using standard ``openrc`` file. (Refer to
http://docs.openstack.org/cli-reference/content/cli_openrc.html on how to retrieve it)

The config can be passed to Shaker rather via the system env:
    ``source openrc``
or via set of CLI parameters ``os-tenant-name``, ``os-username``, ``os-password``,
 ``os-auth-url`` and ``os-region-name``.

In order to be able to control instance scheduling Shaker requires a user with admin
 privileges.


Scenario Explained
------------------

words about how scenario works
