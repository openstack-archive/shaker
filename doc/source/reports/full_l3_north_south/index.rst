.. _openstack_l3_north_south:

OpenStack L3 North-South
************************

This scenario launches pairs of VMs on different compute nodes. VMs are in the
different networks connected via different routers, master accesses slave by
floating ip

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      template: l3_north_south.hot
    description: This scenario launches pairs of VMs on different compute nodes. VMs are
      in the different networks connected via different routers, master accesses slave
      by floating ip
    execution:
      progression: quadratic
      tests:
      - class: flent
        method: tcp_download
        title: Download
      - class: flent
        method: tcp_upload
        title: Upload
      - class: flent
        method: tcp_bidirectional
        title: Bi-directional
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/full_l3_north_south.yaml
    title: OpenStack L3 North-South

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional

.. image:: de257d81-c808-4b8e-bfdb-84c0ae1925e6.*

**Stats**:

===========  =====================  ===================  =============
concurrency  tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
===========  =====================  ===================  =============
          1                 677.49               730.02           2.83
          2                 458.31               464.96           1.10
          5                 186.56               188.01          19.69
         10                  93.53                95.16          52.70
===========  =====================  ===================  =============

Concurrency 1
-------------

**Stats**:

=================  =====================  ===================  =============
node               tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
=================  =====================  ===================  =============
node-7.domain.tld                 677.49               730.02           2.83
=================  =====================  ===================  =============

Concurrency 2
-------------

**Stats**:

=================  =====================  ===================  =============
node               tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
=================  =====================  ===================  =============
node-7.domain.tld                 463.71               358.63           1.17
node-8.domain.tld                 452.91               571.29           1.04
=================  =====================  ===================  =============

Concurrency 5
-------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-17.domain.tld                 131.38               126.00           1.17
node-18.domain.tld                 174.60               248.76          23.30
node-4.domain.tld                  218.45               174.13          48.85
node-7.domain.tld                  252.50               247.47           1.25
node-8.domain.tld                  155.87               143.68          23.88
==================  =====================  ===================  =============

Concurrency 10
--------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-11.domain.tld                  70.72               105.89          32.10
node-13.domain.tld                  41.09                87.66          58.91
node-15.domain.tld                  50.97                66.22          49.67
node-17.domain.tld                 134.96               107.46          49.53
node-18.domain.tld                 195.38                73.91          57.20
node-20.domain.tld                  47.33               109.20          64.02
node-4.domain.tld                   93.19               130.02          69.01
node-5.domain.tld                  160.04                84.94          36.94
node-7.domain.tld                   80.14                53.36          50.13
node-8.domain.tld                   61.44               132.92          59.52
==================  =====================  ===================  =============

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download

.. image:: 43db46b3-0536-4c92-b809-4957afe3a794.*

**Stats**:

===========  =====================  =============
concurrency  tcp_download, Mbits/s  ping_icmp, ms
===========  =====================  =============
          1                 922.30           1.38
          2                 475.85           1.01
          5                 191.92          33.93
         10                  97.23          47.53
===========  =====================  =============

Concurrency 1
-------------

**Stats**:

=================  =====================  =============
node               tcp_download, Mbits/s  ping_icmp, ms
=================  =====================  =============
node-7.domain.tld                 922.30           1.38
=================  =====================  =============

Concurrency 2
-------------

**Stats**:

=================  =====================  =============
node               tcp_download, Mbits/s  ping_icmp, ms
=================  =====================  =============
node-7.domain.tld                 472.46           1.12
node-8.domain.tld                 479.23           0.91
=================  =====================  =============

Concurrency 5
-------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-17.domain.tld                 192.51          39.78
node-18.domain.tld                 189.76          41.85
node-4.domain.tld                  189.54          45.34
node-7.domain.tld                  189.81          41.66
node-8.domain.tld                  198.01           1.04
==================  =====================  =============

Concurrency 10
--------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-11.domain.tld                 161.82          50.27
node-13.domain.tld                  66.99          51.33
node-15.domain.tld                  83.39          54.02
node-17.domain.tld                  62.38          54.22
node-18.domain.tld                  77.17          54.20
node-20.domain.tld                  51.60          54.22
node-4.domain.tld                   97.86          50.46
node-5.domain.tld                   53.75           0.98
node-7.domain.tld                  158.17          54.30
node-8.domain.tld                  159.16          51.26
==================  =====================  =============

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload

.. image:: 73b55d80-654d-438a-8ddd-3d89ce821f38.*

**Stats**:

===========  ===================  =============
concurrency  tcp_upload, Mbits/s  ping_icmp, ms
===========  ===================  =============
          1               890.06           0.86
          2               481.63           8.44
          5               190.86          31.44
         10                97.73          61.75
===========  ===================  =============

Concurrency 1
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-7.domain.tld               890.06           0.86
=================  ===================  =============

Concurrency 2
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-7.domain.tld               476.55           0.75
node-8.domain.tld               486.72          16.13
=================  ===================  =============

Concurrency 5
-------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-17.domain.tld               192.28          41.43
node-18.domain.tld               190.41           0.87
node-4.domain.tld                189.01          38.76
node-7.domain.tld                190.01          36.40
node-8.domain.tld                192.59          39.75
==================  ===================  =============

Concurrency 10
--------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-11.domain.tld               138.34          62.15
node-13.domain.tld               138.37          64.57
node-15.domain.tld                63.27          63.77
node-17.domain.tld                72.49          63.56
node-18.domain.tld               137.22          58.73
node-20.domain.tld                56.73          64.66
node-4.domain.tld                 76.95          60.73
node-5.domain.tld                 68.55          59.09
node-7.domain.tld                 87.67          59.11
node-8.domain.tld                137.68          61.18
==================  ===================  =============

