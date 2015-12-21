===================
CLI Tools Reference
===================

shaker
------

Executes specified scenario in OpenStack cloud, stores results and generates HTML report.

.. literalinclude:: tools/shaker.txt


shaker-spot
-----------

Executes specified scenario from the local node, stores results and generates HTML report.

.. literalinclude:: tools/shaker-spot.txt


shaker-image-builder
--------------------

Builds master image in OpenStack cloud. The image is based on Ubuntu cloud image distro and
configured to run ``shaker-agent``.

.. literalinclude:: tools/shaker-image-builder.txt

shaker-agent
------------

Client-side process that is run inside pre-configured image.

.. literalinclude:: tools/shaker-agent.txt

shaker-report
-------------

Generates report based on raw results stored in JSON format.

.. literalinclude:: tools/shaker-report.txt

shaker-cleanup
--------------

Removes master image from OpenStack cloud.

.. literalinclude:: tools/shaker-cleanup.txt
