.. _openstack_l2_dense:

OpenStack L2 Dense
******************

This scenario launches several pairs of VMs on the same compute node. VM are plugged into the same private network. Useful for testing performance degradation when the number of VMs grows.

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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/networking/dense_l2.yaml
    title: OpenStack L2 Dense
    

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional
    

.. image:: a0223a0a-7548-40a5-9560-fd3388978f08.*

**Stats**:

===========  ==================  ==========================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
===========  ==================  ==========================  ========================  
          1               1.198                    9621.427                  9704.357  
          2               1.867                    6330.361                  6262.754  
          3               2.552                    4598.514                  4529.138  
          4               3.523                    3279.710                  3291.723  
          5               4.555                    2516.362                  2516.939  
          6               5.712                    2002.734                  2003.242  
          7               6.966                    1638.642                  1652.104  
          8               7.805                    1408.165                  1419.220  
===========  ==================  ==========================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               1.198                    9621.427                  9704.357  
=================  ==================  ==========================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               1.878                    6365.885                  6320.517  
node-6.domain.tld               1.857                    6294.836                  6204.991  
=================  ==================  ==========================  ========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               2.636                    4669.996                  4664.194  
node-6.domain.tld               2.627                    4568.320                  4494.731  
node-6.domain.tld               2.392                    4557.228                  4428.487  
=================  ==================  ==========================  ========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               3.683                    3259.306                  3287.131  
node-6.domain.tld               3.826                    3257.170                  3226.800  
node-6.domain.tld               3.327                    3304.134                  3338.812  
node-6.domain.tld               3.256                    3298.231                  3314.148  
=================  ==================  ==========================  ========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               4.808                    2540.439                  2520.881  
node-6.domain.tld               5.035                    2550.881                  2583.927  
node-6.domain.tld               4.141                    2486.479                  2480.277  
node-6.domain.tld               3.974                    2520.539                  2515.503  
node-6.domain.tld               4.815                    2483.471                  2484.108  
=================  ==================  ==========================  ========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               5.896                    1961.103                  1984.380  
node-6.domain.tld               5.188                    1986.602                  1964.583  
node-6.domain.tld               6.153                    2043.138                  2047.810  
node-6.domain.tld               6.024                    1990.229                  1965.508  
node-6.domain.tld               6.024                    1982.947                  2006.110  
node-6.domain.tld               4.988                    2052.382                  2051.062  
=================  ==================  ==========================  ========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               7.217                    1624.425                  1648.094  
node-6.domain.tld               7.722                    1691.706                  1672.049  
node-6.domain.tld               6.224                    1631.462                  1648.616  
node-6.domain.tld               7.102                    1609.214                  1646.555  
node-6.domain.tld               7.116                    1615.920                  1620.923  
node-6.domain.tld               5.991                    1614.438                  1628.191  
node-6.domain.tld               7.389                    1683.330                  1700.301  
=================  ==================  ==========================  ========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-6.domain.tld               8.127                    1355.436                  1368.430  
node-6.domain.tld               8.192                    1362.260                  1367.905  
node-6.domain.tld               8.099                    1360.852                  1354.818  
node-6.domain.tld               7.356                    1403.670                  1401.411  
node-6.domain.tld               7.062                    1377.463                  1421.642  
node-6.domain.tld               7.744                    1395.065                  1399.405  
node-6.domain.tld               7.861                    1381.552                  1380.697  
node-6.domain.tld               8.002                    1629.023                  1659.454  
=================  ==================  ==========================  ========================  

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download
    

.. image:: 883be6c4-bcb8-4297-9b0f-34aa3006ffac.*

**Stats**:

===========  ==================  ==========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  
===========  ==================  ==========================  
          1               0.636                   15237.497  
          2               0.948                   11753.030  
          3               1.083                   10193.872  
          4               1.832                    7311.929  
          5               2.700                    5592.604  
          6               2.905                    4488.039  
          7               3.635                    3696.833  
          8               4.421                    3166.107  
===========  ==================  ==========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               0.636                   15237.497  
=================  ==================  ==========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               0.955                   11632.380  
node-6.domain.tld               0.941                   11873.681  
=================  ==================  ==========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               1.184                   10014.043  
node-6.domain.tld               1.070                   10284.539  
node-6.domain.tld               0.994                   10283.036  
=================  ==================  ==========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               1.838                    7282.475  
node-6.domain.tld               1.895                    7257.453  
node-6.domain.tld               1.881                    7291.693  
node-6.domain.tld               1.716                    7416.097  
=================  ==================  ==========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               2.671                    5547.215  
node-6.domain.tld               2.597                    5518.593  
node-6.domain.tld               3.239                    5583.559  
node-6.domain.tld               2.611                    5753.134  
node-6.domain.tld               2.382                    5560.520  
=================  ==================  ==========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               2.824                    4502.026  
node-6.domain.tld               2.940                    4565.028  
node-6.domain.tld               2.682                    4458.908  
node-6.domain.tld               2.829                    4493.589  
node-6.domain.tld               3.299                    4430.716  
node-6.domain.tld               2.855                    4477.964  
=================  ==================  ==========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               3.564                    3668.971  
node-6.domain.tld               4.153                    3789.900  
node-6.domain.tld               3.186                    3606.681  
node-6.domain.tld               4.155                    3666.121  
node-6.domain.tld               3.245                    3753.064  
node-6.domain.tld               4.083                    3707.976  
node-6.domain.tld               3.061                    3685.120  
=================  ==================  ==========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-6.domain.tld               4.285                    3107.039  
node-6.domain.tld               4.892                    3450.021  
node-6.domain.tld               4.017                    3093.748  
node-6.domain.tld               4.801                    3081.134  
node-6.domain.tld               3.678                    3129.716  
node-6.domain.tld               4.451                    3188.587  
node-6.domain.tld               4.519                    3068.883  
node-6.domain.tld               4.725                    3209.730  
=================  ==================  ==========================  

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload
    

.. image:: ee14bebf-16c8-4421-ade5-1759c5df3e8e.*

**Stats**:

===========  ==================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_upload, Mbits/s  
===========  ==================  ========================  
          1               0.758                 16164.292  
          2               1.106                 11832.457  
          3               1.494                  9988.862  
          4               2.583                  7146.267  
          5               2.905                  5548.757  
          6               3.532                  4465.029  
          7               3.851                  3701.963  
          8               4.470                  3145.423  
===========  ==================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               0.758                 16164.292  
=================  ==================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               1.106                 11898.270  
node-6.domain.tld               1.106                 11766.644  
=================  ==================  ========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               1.691                 10005.984  
node-6.domain.tld               1.535                  9859.361  
node-6.domain.tld               1.256                 10101.240  
=================  ==================  ========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               2.770                  7181.583  
node-6.domain.tld               2.466                  7157.957  
node-6.domain.tld               2.656                  7042.016  
node-6.domain.tld               2.441                  7203.510  
=================  ==================  ========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               2.596                  5423.445  
node-6.domain.tld               2.969                  5666.079  
node-6.domain.tld               2.868                  5610.239  
node-6.domain.tld               3.383                  5503.635  
node-6.domain.tld               2.708                  5540.388  
=================  ==================  ========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               3.711                  4490.940  
node-6.domain.tld               3.787                  4437.253  
node-6.domain.tld               3.327                  4583.273  
node-6.domain.tld               3.468                  4516.928  
node-6.domain.tld               3.006                  4497.667  
node-6.domain.tld               3.891                  4264.112  
=================  ==================  ========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               3.574                  3694.315  
node-6.domain.tld               3.798                  3658.241  
node-6.domain.tld               3.395                  3684.001  
node-6.domain.tld               3.577                  3778.586  
node-6.domain.tld               4.279                  3731.529  
node-6.domain.tld               3.616                  3667.923  
node-6.domain.tld               4.721                  3699.144  
=================  ==================  ========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-6.domain.tld               4.303                  3217.616  
node-6.domain.tld               4.923                  3086.229  
node-6.domain.tld               4.802                  3175.518  
node-6.domain.tld               4.617                  3131.539  
node-6.domain.tld               4.580                  3049.197  
node-6.domain.tld               4.450                  3090.433  
node-6.domain.tld               3.671                  3099.691  
node-6.domain.tld               4.415                  3313.163  
=================  ==================  ========================  

