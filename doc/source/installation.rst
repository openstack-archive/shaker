============
Installation
============

Installation in Python environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shaker is distributed as Python package and available through PyPi (https://pypi.python.org/pypi/pyshaker/).
It is recommended to be installed inside virtualenv.

.. code::

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install pyshaker


Installation on Ubuntu Cloud Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Installation on fresh system requires additional libraries needed by some of dependencies.

.. code::

    $ sudo apt-add-repository "deb http://nova.clouds.archive.ubuntu.com/ubuntu/ trusty multiverse"
    $ sudo apt-get update
    $ sudo apt-get -y install python-dev libzmq-dev
    $ wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py
    $ sudo pip install pbr pyshaker
    $ shaker --help


OpenStack Deployment
^^^^^^^^^^^^^^^^^^^^

.. image:: images/architecture.*

Requirements:

    * Computer where Shaker is executed should be routable from OpenStack instances and
      should have open port to accept connections from agents running on instances

For full features support it is advised to run Shaker by admin user. However
with some limitations it works for non-admin user - see :ref:`non_admin_mode` for details.


Build base image
^^^^^^^^^^^^^^^^

Automatic build in OpenStack
----------------------------

.. note::
    This method requires Glance v.1 API; the base image is downloaded directly
    from Internet into Glance.

Build the master image. The process downloads Ubuntu cloud image, installs all necessary packages and stores
snapshot into Glance. This snapshot is used by ``shaker`` as base of instances.

.. code::

    $ shaker-image-builder


Manual build with disk-image-builder
------------------------------------

Shaker image can also be built using `diskimage-builder`_ tool.

    #. Install disk-image-builder. Refer to `diskimage-builder installation`_
    #. Clone Shaker repo:
       ``git clone git://git.openstack.org/openstack/shaker``
    #. Add search path for diskimage-builder elements:
       ``export ELEMENTS_PATH=shaker/shaker/resources/image_elements``
    #. Build the image based on Ubuntu Xenial:
       ``disk-image-create -o shaker-image.qcow2 ubuntu vm shaker``
    #. Upload image into Glance:
       ``openstack image create --public --file shaker-image.qcow2 --disk-format qcow2 shaker-image``
    #. Create flavor:
       ``openstack flavor create --ram 512 --disk 3 --vcpus 1 shaker-flavor``


.. _non_admin_mode:

Running Shaker by non-admin user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While the full feature set is available when Shaker is run by admin user,
it works with some limitations for non-admin user too.


Image builder limitations
-------------------------

Image builder requires flavor name to be specified via command line
parameter `--flavor-name`. Create flavor prior running Shaker, or choose
one that satisfies instance template requirements. For Ubuntu-based image
the requirement is 512 Mb RAM, 3 Gb disk and 1 CPU


Execution limitations
---------------------

Non-admin user has no permissions to list compute nodes and to deploy instances
to particular compute nodes.

When instances need to be deployed on low number of compute nodes it is possible
to use server groups and specify anti-affinity policy within them. Note however that
server group size is limited by `quota_server_group_members` parameter in `nova.conf`.
The following is part of Heat template adds server groups.

Add to resources section::

  server_group:
    type: OS::Nova::ServerGroup
    properties:
      name: {{ unique }}_server_group
      policies: [ 'anti-affinity' ]

Add attribute to server definition::

      scheduler_hints:
        group: { get_resource: server_group }

The similar patch is needed to implement dense scenarios. The difference is
in server group policy, it should be `'affinity'`.

Alternative approach is to specify number of compute nodes. Note that the
number must always be specified. If Nova distributes instances evenly (or with
normal random distribution) then the chances that instances are placed on
unique nodes are quite high (well, there will be collisions due to
https://en.wikipedia.org/wiki/Birthday_problem, so expect that number of
unique pair will be lower than specified number of compute nodes).


Non-OpenStack Deployment (aka Spot mode)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To run scenarios against remote nodes (``shaker-spot`` command) install shaker on the local host.
Make sure all necessary tools are installed too. Refer to :ref:`spot_scenarios` for more details.


Run Shaker against OpenStack deployed by Fuel-CCP on Kubernetes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shaker can be run in Kubernetes environment and can execute scenarios against
OpenStack deployed by Fuel-CCP tool.

Shaker app consists of *service*:

  .. literalinclude:: k8s/shaker-svc.yaml
    :language: yaml

and *pod*:

  .. literalinclude:: k8s/shaker-pod.yaml
    :language: yaml

You may need to change values for variables defined in config files:

  * `SHAKER_SERVER_ENDPOINT` should point to external address of Kubernetes cluster,
    and OpenStack instances must have access to it
  * `OS_***` parameters describe connection to Keystone endpoint
  * `SHAKER_SCENARIO` needs to be altered to run the needed scenario
  * Pod is configured to write logs into /tmp on the node that hosts the pod
  * `port`, `nodePort` and `targetPort` must be equal and not to conflict with
    other exposed services


.. references:

.. _diskimage-builder: https://docs.openstack.org/diskimage-builder/latest/
.. _diskimage-builder installation: https://docs.openstack.org/diskimage-builder/latest/user_guide/installation.html
