.. _openstack_l3_east_west_dense:

OpenStack L3 East-West Dense
****************************

This scenario launches pairs of VMs in different networks connected to one
router (L3 east-west)

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - double_room
      - density: 8
      - compute_nodes: 1
      template: l3_east_west.hot
    description: This scenario launches pairs of VMs in different networks connected to
      one router (L3 east-west)
    execution:
      progression: linear
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/dense_l3_east_west.yaml
    title: OpenStack L3 East-West Dense

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional

.. image:: dbe5eb6f-351b-4297-88a8-5130f67064c5.*

**Stats**:

===========  ===================  =============  =====================
concurrency  tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
===========  ===================  =============  =====================
          1              2814.04           3.65                2862.18
          2              2007.10           5.09                2118.44
          3              1482.64           8.04                1305.91
          4              1170.08           8.35                1141.41
          5               909.19          10.51                 918.53
          6               799.28          12.35                 759.03
          7               673.86          14.81                 666.51
          8               596.48          16.11                 581.02
===========  ===================  =============  =====================

Concurrency 1
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld              2814.04           3.65                2862.18
=================  ===================  =============  =====================

Concurrency 2
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld              2080.99           4.29                2483.08
node-5.domain.tld              1933.21           5.89                1753.80
=================  ===================  =============  =====================

Concurrency 3
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld              1238.39          10.64                1045.61
node-5.domain.tld              2016.54           5.48                1768.01
node-5.domain.tld              1192.99           8.02                1104.12
=================  ===================  =============  =====================

Concurrency 4
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld              1177.99           7.54                1289.99
node-5.domain.tld              1135.60           8.45                1112.07
node-5.domain.tld              1204.90           9.21                1025.01
node-5.domain.tld              1161.82           8.19                1138.58
=================  ===================  =============  =====================

Concurrency 5
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld               937.75          10.72                 859.38
node-5.domain.tld               984.40           9.69                 999.06
node-5.domain.tld               884.40          12.42                 892.02
node-5.domain.tld               878.76          10.17                 986.22
node-5.domain.tld               860.63           9.55                 855.98
=================  ===================  =============  =====================

Concurrency 6
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld               800.83          14.16                 800.62
node-5.domain.tld               907.79          12.76                 774.30
node-5.domain.tld               789.24          12.71                 751.34
node-5.domain.tld               778.34          11.16                 790.35
node-5.domain.tld               778.92          10.96                 769.99
node-5.domain.tld               740.54          12.37                 667.58
=================  ===================  =============  =====================

Concurrency 7
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld               719.54          16.54                 660.84
node-5.domain.tld               722.22          14.58                 625.52
node-5.domain.tld               626.60          14.66                 726.26
node-5.domain.tld               684.59          13.92                 682.97
node-5.domain.tld               682.67          13.97                 728.80
node-5.domain.tld               649.98          15.72                 552.49
node-5.domain.tld               631.41          14.30                 688.73
=================  ===================  =============  =====================

Concurrency 8
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-5.domain.tld               572.87          14.97                 607.17
node-5.domain.tld               558.98          15.34                 631.26
node-5.domain.tld               589.19          17.86                 583.32
node-5.domain.tld               595.93          15.09                 537.40
node-5.domain.tld               619.96          16.15                 549.46
node-5.domain.tld               566.98          17.50                 585.90
node-5.domain.tld               628.83          15.26                 582.33
node-5.domain.tld               639.13          16.70                 571.30
=================  ===================  =============  =====================

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download

.. image:: b301136d-c6d5-4eb3-8942-be2041bde8e2.*

**Stats**:

===========  =============  =====================
concurrency  ping_icmp, ms  tcp_download, Mbits/s
===========  =============  =====================
          1           2.61                3232.05
          2           3.46                3265.07
          3           4.14                2678.01
          4           4.34                2192.83
          5           5.77                1805.04
          6           6.83                1520.49
          7           6.68                1296.37
          8           8.04                1169.80
===========  =============  =====================

Concurrency 1
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           2.61                3232.05
=================  =============  =====================

Concurrency 2
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           3.50                3145.52
node-5.domain.tld           3.41                3384.62
=================  =============  =====================

Concurrency 3
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           4.10                2752.96
node-5.domain.tld           3.57                2717.00
node-5.domain.tld           4.75                2564.08
=================  =============  =====================

Concurrency 4
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           4.79                2105.32
node-5.domain.tld           4.27                2252.28
node-5.domain.tld           4.76                2144.97
node-5.domain.tld           3.55                2268.76
=================  =============  =====================

Concurrency 5
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           6.57                1742.67
node-5.domain.tld           5.39                1868.02
node-5.domain.tld           5.24                1697.80
node-5.domain.tld           6.39                1952.90
node-5.domain.tld           5.24                1763.82
=================  =============  =====================

Concurrency 6
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           6.80                1347.71
node-5.domain.tld           7.98                1406.02
node-5.domain.tld           6.81                1546.89
node-5.domain.tld           5.43                1662.43
node-5.domain.tld           7.36                1513.16
node-5.domain.tld           6.58                1646.74
=================  =============  =====================

Concurrency 7
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           5.44                1524.59
node-5.domain.tld           6.32                 985.88
node-5.domain.tld           6.65                1551.91
node-5.domain.tld           7.44                1444.54
node-5.domain.tld           6.60                1492.27
node-5.domain.tld           7.01                 965.67
node-5.domain.tld           7.26                1109.73
=================  =============  =====================

Concurrency 8
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-5.domain.tld           6.66                1361.59
node-5.domain.tld           7.88                1041.82
node-5.domain.tld           8.44                1263.24
node-5.domain.tld           8.40                1052.99
node-5.domain.tld           9.14                1218.77
node-5.domain.tld           7.72                1166.68
node-5.domain.tld           6.83                1189.83
node-5.domain.tld           9.23                1063.47
=================  =============  =====================

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload

.. image:: fa959708-db0c-40be-9b11-391064e6a003.*

**Stats**:

===========  ===================  =============
concurrency  tcp_upload, Mbits/s  ping_icmp, ms
===========  ===================  =============
          1              3844.43           2.81
          2              3396.30           3.11
          3              2321.55           3.30
          4              2140.43           4.10
          5              1730.21           5.14
          6              1246.42           4.35
          7              1329.00           6.97
          8              1134.45           7.98
===========  ===================  =============

Concurrency 1
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              3844.43           2.81
=================  ===================  =============

Concurrency 2
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              3482.66           2.78
node-5.domain.tld              3309.94           3.44
=================  ===================  =============

Concurrency 3
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              2942.33           2.80
node-5.domain.tld              2025.66           3.07
node-5.domain.tld              1996.67           4.05
=================  ===================  =============

Concurrency 4
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              1833.08           3.68
node-5.domain.tld              2506.52           4.41
node-5.domain.tld              2223.73           3.82
node-5.domain.tld              1998.38           4.49
=================  ===================  =============

Concurrency 5
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              1527.11           4.09
node-5.domain.tld              1877.01           3.86
node-5.domain.tld              1851.41           4.48
node-5.domain.tld              1944.21           6.07
node-5.domain.tld              1451.29           7.21
=================  ===================  =============

Concurrency 6
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld               755.12          14.41
node-5.domain.tld              2021.84           2.26
node-5.domain.tld               928.22           1.26
node-5.domain.tld              2076.70           3.16
node-5.domain.tld               848.13           1.59
node-5.domain.tld               848.49           3.42
=================  ===================  =============

Concurrency 7
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              1330.81           8.47
node-5.domain.tld              1497.74           5.40
node-5.domain.tld              1297.62           6.61
node-5.domain.tld              1207.32           7.11
node-5.domain.tld              1388.78           8.44
node-5.domain.tld              1210.06           6.73
node-5.domain.tld              1370.67           6.01
=================  ===================  =============

Concurrency 8
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-5.domain.tld              1131.88           8.76
node-5.domain.tld              1058.38           7.68
node-5.domain.tld              1067.14           7.80
node-5.domain.tld              1350.97           7.68
node-5.domain.tld               985.73           6.97
node-5.domain.tld              1060.46           7.20
node-5.domain.tld              1117.55           9.80
node-5.domain.tld              1303.53           7.92
=================  ===================  =============

