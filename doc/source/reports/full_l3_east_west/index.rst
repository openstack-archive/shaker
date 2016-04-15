.. _openstack_l3_east_west:

OpenStack L3 East-West
**********************

This scenario launches pairs of VMs in different networks connected to one
router (L3 east-west)

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      template: l3_east_west.hot
    description: This scenario launches pairs of VMs in different networks connected to
      one router (L3 east-west)
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/full_l3_east_west.yaml
    title: OpenStack L3 East-West

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional

.. image:: 971e06b7-59f2-4154-976c-1db0e7f7645f.*

**Stats**:

===========  =====================  ===================  =============
concurrency  tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
===========  =====================  ===================  =============
          1                3816.62              3474.93           2.92
          2                2264.43              2632.60           4.88
          5                1016.47               991.04           7.11
         10                 491.52               514.84           9.54
===========  =====================  ===================  =============

Concurrency 1
-------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-13.domain.tld                3816.62              3474.93           2.92
==================  =====================  ===================  =============

Concurrency 2
-------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-13.domain.tld                2423.30              2639.19           6.56
node-15.domain.tld                2105.57              2626.00           3.20
==================  =====================  ===================  =============

Concurrency 5
-------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-13.domain.tld                 971.69               839.75          10.07
node-15.domain.tld                1490.89               948.82           6.33
node-20.domain.tld                 758.93               889.14           5.69
node-4.domain.tld                  786.01              1125.13           7.69
node-5.domain.tld                 1074.82              1152.35           5.75
==================  =====================  ===================  =============

Concurrency 10
--------------

**Stats**:

==================  =====================  ===================  =============
node                tcp_download, Mbits/s  tcp_upload, Mbits/s  ping_icmp, ms
==================  =====================  ===================  =============
node-11.domain.tld                 752.08               763.63           9.52
node-13.domain.tld                 320.14               935.47          13.50
node-15.domain.tld                 354.13               506.37           5.85
node-17.domain.tld                 902.35               346.84          13.27
node-18.domain.tld                 790.13               358.23          13.42
node-20.domain.tld                 378.52               360.62           5.99
node-4.domain.tld                  346.47               437.56           9.38
node-5.domain.tld                  367.27               706.91           5.70
node-7.domain.tld                  347.72               392.19           9.47
node-8.domain.tld                  356.42               340.56           9.33
==================  =====================  ===================  =============

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download

.. image:: 7db77fbd-ac1b-4f48-9200-992578593598.*

**Stats**:

===========  =====================  =============
concurrency  tcp_download, Mbits/s  ping_icmp, ms
===========  =====================  =============
          1                4049.22           0.96
          2                4792.05           2.09
          5                1858.96           3.94
         10                 999.79           7.62
===========  =====================  =============

Concurrency 1
-------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-13.domain.tld                4049.22           0.96
==================  =====================  =============

Concurrency 2
-------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-13.domain.tld                5126.86           2.81
node-15.domain.tld                4457.24           1.38
==================  =====================  =============

Concurrency 5
-------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-13.domain.tld                1475.56           4.33
node-15.domain.tld                1486.69           7.91
node-20.domain.tld                2385.87           2.15
node-4.domain.tld                 2470.58           3.87
node-5.domain.tld                 1476.10           1.42
==================  =====================  =============

Concurrency 10
--------------

**Stats**:

==================  =====================  =============
node                tcp_download, Mbits/s  ping_icmp, ms
==================  =====================  =============
node-11.domain.tld                 842.15           7.68
node-13.domain.tld                1180.86           8.50
node-15.domain.tld                1496.95           6.76
node-17.domain.tld                1018.10           8.80
node-18.domain.tld                 979.22           8.77
node-20.domain.tld                 893.75           6.47
node-4.domain.tld                  846.17           7.52
node-5.domain.tld                  822.03           6.59
node-7.domain.tld                  866.79           7.42
node-8.domain.tld                 1051.91           7.65
==================  =====================  =============

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload

.. image:: a5cec469-249a-4d9a-ad2d-51b5ce38de7e.*

**Stats**:

===========  ===================  =============
concurrency  tcp_upload, Mbits/s  ping_icmp, ms
===========  ===================  =============
          1              4209.99           0.79
          2              3849.74           2.98
          5              1996.74           5.47
         10              1009.21           8.05
===========  ===================  =============

Concurrency 1
-------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-13.domain.tld              4209.99           0.79
==================  ===================  =============

Concurrency 2
-------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-13.domain.tld              4086.94           2.07
node-15.domain.tld              3612.54           3.89
==================  ===================  =============

Concurrency 5
-------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-13.domain.tld              2053.60           9.05
node-15.domain.tld              1525.48           3.71
node-20.domain.tld              1463.32           3.94
node-4.domain.tld               3485.97           6.73
node-5.domain.tld               1455.31           3.96
==================  ===================  =============

Concurrency 10
--------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-11.domain.tld               830.32           8.19
node-13.domain.tld               720.02          11.14
node-15.domain.tld               807.43           4.96
node-17.domain.tld               956.33          11.02
node-18.domain.tld               926.50          11.21
node-20.domain.tld              1272.34           5.04
node-4.domain.tld               1371.94           8.07
node-5.domain.tld               1306.22           4.91
node-7.domain.tld                906.63           7.85
node-8.domain.tld                994.41           8.08
==================  ===================  =============

