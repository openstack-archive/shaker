.. _openstack_l2_dense:

OpenStack L2 Dense
******************

This scenario launches several pairs of VMs on the same compute node. VM are
plugged into the same private network. Useful for testing performance
degradation when the number of VMs grows.

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - double_room
      - density: 8
      - compute_nodes: 1
      template: l2.hot
    description: This scenario launches several pairs of VMs on the same compute node.
      VM are plugged into the same private network. Useful for testing performance degradation
      when the number of VMs grows.
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/dense_l2.yaml
    title: OpenStack L2 Dense

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional

.. image:: ba3c8569-7318-4dc6-ba70-1a45cee0e3e6.*

**Stats**:

===========  =============  =====================  ===================
concurrency  ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
===========  =============  =====================  ===================
          1           1.20                9621.43              9704.36
          2           1.87                6330.36              6262.75
          3           2.55                4598.51              4529.14
          4           3.52                3279.71              3291.72
          5           4.55                2516.36              2516.94
          6           5.71                2002.73              2003.24
          7           6.97                1638.64              1652.10
          8           7.81                1408.17              1419.22
===========  =============  =====================  ===================

Concurrency 1
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           1.20                9621.43              9704.36
=================  =============  =====================  ===================

Concurrency 2
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           1.86                6294.84              6204.99
node-6.domain.tld           1.88                6365.88              6320.52
=================  =============  =====================  ===================

Concurrency 3
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           2.39                4557.23              4428.49
node-6.domain.tld           2.64                4670.00              4664.19
node-6.domain.tld           2.63                4568.32              4494.73
=================  =============  =====================  ===================

Concurrency 4
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           3.68                3259.31              3287.13
node-6.domain.tld           3.26                3298.23              3314.15
node-6.domain.tld           3.83                3257.17              3226.80
node-6.domain.tld           3.33                3304.13              3338.81
=================  =============  =====================  ===================

Concurrency 5
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           5.04                2550.88              2583.93
node-6.domain.tld           4.14                2486.48              2480.28
node-6.domain.tld           3.97                2520.54              2515.50
node-6.domain.tld           4.82                2483.47              2484.11
node-6.domain.tld           4.81                2540.44              2520.88
=================  =============  =====================  ===================

Concurrency 6
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           5.90                1961.10              1984.38
node-6.domain.tld           4.99                2052.38              2051.06
node-6.domain.tld           6.02                1990.23              1965.51
node-6.domain.tld           5.19                1986.60              1964.58
node-6.domain.tld           6.02                1982.95              2006.11
node-6.domain.tld           6.15                2043.14              2047.81
=================  =============  =====================  ===================

Concurrency 7
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           7.39                1683.33              1700.30
node-6.domain.tld           5.99                1614.44              1628.19
node-6.domain.tld           6.22                1631.46              1648.62
node-6.domain.tld           7.12                1615.92              1620.92
node-6.domain.tld           7.22                1624.42              1648.09
node-6.domain.tld           7.10                1609.21              1646.56
node-6.domain.tld           7.72                1691.71              1672.05
=================  =============  =====================  ===================

Concurrency 8
-------------

**Stats**:

=================  =============  =====================  ===================
node               ping_icmp, ms  tcp_download, Mbits/s  tcp_upload, Mbits/s
=================  =============  =====================  ===================
node-6.domain.tld           7.86                1381.55              1380.70
node-6.domain.tld           8.10                1360.85              1354.82
node-6.domain.tld           8.00                1629.02              1659.45
node-6.domain.tld           7.36                1403.67              1401.41
node-6.domain.tld           8.19                1362.26              1367.91
node-6.domain.tld           7.74                1395.07              1399.40
node-6.domain.tld           7.06                1377.46              1421.64
node-6.domain.tld           8.13                1355.44              1368.43
=================  =============  =====================  ===================

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download

.. image:: 73b640de-a11f-4876-9494-11a2641193b5.*

**Stats**:

===========  =============  =====================
concurrency  ping_icmp, ms  tcp_download, Mbits/s
===========  =============  =====================
          1           0.64               15237.50
          2           0.95               11753.03
          3           1.08               10193.87
          4           1.83                7311.93
          5           2.70                5592.60
          6           2.90                4488.04
          7           3.64                3696.83
          8           4.42                3166.11
===========  =============  =====================

Concurrency 1
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           0.64               15237.50
=================  =============  =====================

Concurrency 2
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           0.96               11632.38
node-6.domain.tld           0.94               11873.68
=================  =============  =====================

Concurrency 3
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           1.07               10284.54
node-6.domain.tld           1.18               10014.04
node-6.domain.tld           0.99               10283.04
=================  =============  =====================

Concurrency 4
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           1.90                7257.45
node-6.domain.tld           1.84                7282.47
node-6.domain.tld           1.72                7416.10
node-6.domain.tld           1.88                7291.69
=================  =============  =====================

Concurrency 5
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           2.60                5518.59
node-6.domain.tld           2.61                5753.13
node-6.domain.tld           2.38                5560.52
node-6.domain.tld           3.24                5583.56
node-6.domain.tld           2.67                5547.21
=================  =============  =====================

Concurrency 6
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           2.68                4458.91
node-6.domain.tld           2.94                4565.03
node-6.domain.tld           2.83                4493.59
node-6.domain.tld           2.82                4502.03
node-6.domain.tld           3.30                4430.72
node-6.domain.tld           2.85                4477.96
=================  =============  =====================

Concurrency 7
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           3.06                3685.12
node-6.domain.tld           4.15                3789.90
node-6.domain.tld           3.56                3668.97
node-6.domain.tld           3.19                3606.68
node-6.domain.tld           3.25                3753.06
node-6.domain.tld           4.08                3707.98
node-6.domain.tld           4.15                3666.12
=================  =============  =====================

Concurrency 8
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-6.domain.tld           4.45                3188.59
node-6.domain.tld           3.68                3129.72
node-6.domain.tld           4.80                3081.13
node-6.domain.tld           4.02                3093.75
node-6.domain.tld           4.72                3209.73
node-6.domain.tld           4.52                3068.88
node-6.domain.tld           4.28                3107.04
node-6.domain.tld           4.89                3450.02
=================  =============  =====================

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload

.. image:: 69d3be4d-88d9-49de-8d02-74c90b636410.*

**Stats**:

===========  =============  ===================
concurrency  ping_icmp, ms  tcp_upload, Mbits/s
===========  =============  ===================
          1           0.76             16164.29
          2           1.11             11832.46
          3           1.49              9988.86
          4           2.58              7146.27
          5           2.90              5548.76
          6           3.53              4465.03
          7           3.85              3701.96
          8           4.47              3145.42
===========  =============  ===================

Concurrency 1
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           0.76             16164.29
=================  =============  ===================

Concurrency 2
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           1.11             11898.27
node-6.domain.tld           1.11             11766.64
=================  =============  ===================

Concurrency 3
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           1.69             10005.98
node-6.domain.tld           1.54              9859.36
node-6.domain.tld           1.26             10101.24
=================  =============  ===================

Concurrency 4
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           2.66              7042.02
node-6.domain.tld           2.77              7181.58
node-6.domain.tld           2.44              7203.51
node-6.domain.tld           2.47              7157.96
=================  =============  ===================

Concurrency 5
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           2.87              5610.24
node-6.domain.tld           2.60              5423.45
node-6.domain.tld           2.71              5540.39
node-6.domain.tld           3.38              5503.63
node-6.domain.tld           2.97              5666.08
=================  =============  ===================

Concurrency 6
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           3.33              4583.27
node-6.domain.tld           3.79              4437.25
node-6.domain.tld           3.01              4497.67
node-6.domain.tld           3.47              4516.93
node-6.domain.tld           3.71              4490.94
node-6.domain.tld           3.89              4264.11
=================  =============  ===================

Concurrency 7
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           4.72              3699.14
node-6.domain.tld           3.39              3684.00
node-6.domain.tld           3.57              3694.32
node-6.domain.tld           3.58              3778.59
node-6.domain.tld           3.62              3667.92
node-6.domain.tld           3.80              3658.24
node-6.domain.tld           4.28              3731.53
=================  =============  ===================

Concurrency 8
-------------

**Stats**:

=================  =============  ===================
node               ping_icmp, ms  tcp_upload, Mbits/s
=================  =============  ===================
node-6.domain.tld           4.42              3313.16
node-6.domain.tld           4.45              3090.43
node-6.domain.tld           4.58              3049.20
node-6.domain.tld           3.67              3099.69
node-6.domain.tld           4.30              3217.62
node-6.domain.tld           4.92              3086.23
node-6.domain.tld           4.62              3131.54
node-6.domain.tld           4.80              3175.52
=================  =============  ===================

