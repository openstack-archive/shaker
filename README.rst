Shaker
======

Shake VMs with our sheer-class tests!

Installation
------------

The tool consists of a single server running on master node and set of dynamically
provisioned agents. In order to run the server needs to know OpenStack parameters
(credentials, auth_url), they can be set via environment (e.g. by sourcing openrc file)
or via parameters.

To install:
 1. ``git clone git://git.openstack.org/stackforge/shaker``
 2. ``python setup.py install`` - installs the tool and all its python dependencies
 3. ``shaker-image-builder`` - builds image for agent VMs inside OpenStack

Note: image builder is able to create Nova flavor optimized for the image and this requires
admin user privileges. However if the flavor is already exists then it can be provided via
``flavor-name`` config parameter and the tool executed from an ordinary user.

How to run
----------
 1. ``shaker --server-endpoint <host>:<port> --scenario <scenario-file> --report <report-file>``

During the run the tool deploys topology linked into scenario, spawns instances, distributes
tasks among instances and generates report in HTML format.

All server parameters
---------------------

 * ``server_endpoint = <None>`` - Address for server connections (host:port) (string value)
 * ``os_auth_url`` - Authentication URL, defaults to env[OS_AUTH_URL]. (string value)
 * ``os_tenant_name`` - Authentication tenant name, defaults to env[OS_TENANT_NAME]. (string value)
 * ``os_username`` - Authentication username, defaults to env[OS_USERNAME]. (string value)
 * ``os_password`` - Authentication password, defaults to env[OS_PASSWORD]. (string value)
 * ``os_region_name = RegionOne`` - Authentication region name, defaults to env[OS_REGION_NAME]. (string value)
 * ``external_net`` - Name or ID of external network. If not set the network is chosen randomly. (string value)
 * ``image_name = shaker-image`` - Name of image to use. The default is created by shaker-image-builder (string value)
 * ``flavor_name = shaker-flavor`` - Name of image flavor. The default is created by shaker-image-builder (string value)
 * ``scenario = <None>`` - Scenario file name (string value)
 * ``report = <None>`` - Report file name. If not specified print to stdout (string value)
 * ``report_template = shaker/engine/report.template`` - Report template file name (Jinja format) (string value)
