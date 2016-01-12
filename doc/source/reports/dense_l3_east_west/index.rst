.. _openstack_l3_east_west_dense:

OpenStack L3 East-West Dense
****************************

This scenario launches pairs of VMs in different networks connected to one router (L3 east-west)

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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/networking/dense_l3_east_west.yaml
    title: OpenStack L3 East-West Dense
    

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional
    

.. image:: 8b975b6e-4035-4049-b28f-40b9047c0ec2.*

**Stats**:

===========  ==================  ==========================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
===========  ==================  ==========================  ========================  
          1               3.646                    2862.182                  2814.040  
          2               5.092                    2118.442                  2007.098  
          3               8.045                    1305.913                  1482.640  
          4               8.348                    1141.414                  1170.079  
          5              10.508                     918.531                   909.190  
          6              12.352                     759.028                   799.276  
          7              14.814                     666.514                   673.858  
          8              16.109                     581.018                   596.482  
===========  ==================  ==========================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld               3.646                    2862.182                  2814.040  
=================  ==================  ==========================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld               4.293                    2483.083                  2080.985  
node-5.domain.tld               5.890                    1753.801                  1933.210  
=================  ==================  ==========================  ========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld               5.476                    1768.005                  2016.537  
node-5.domain.tld               8.018                    1104.121                  1192.990  
node-5.domain.tld              10.639                    1045.612                  1238.394  
=================  ==================  ==========================  ========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld               7.545                    1289.990                  1177.994  
node-5.domain.tld               9.208                    1025.012                  1204.903  
node-5.domain.tld               8.452                    1112.074                  1135.598  
node-5.domain.tld               8.186                    1138.581                  1161.822  
=================  ==================  ==========================  ========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld              10.173                     986.216                   878.764  
node-5.domain.tld              10.715                     859.380                   937.749  
node-5.domain.tld               9.691                     999.059                   984.405  
node-5.domain.tld               9.546                     855.982                   860.630  
node-5.domain.tld              12.416                     892.018                   884.402  
=================  ==================  ==========================  ========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld              11.156                     790.347                   778.338  
node-5.domain.tld              14.157                     800.616                   800.827  
node-5.domain.tld              12.760                     774.297                   907.793  
node-5.domain.tld              12.366                     667.580                   740.540  
node-5.domain.tld              12.710                     751.342                   789.238  
node-5.domain.tld              10.964                     769.986                   778.921  
=================  ==================  ==========================  ========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld              16.536                     660.836                   719.535  
node-5.domain.tld              14.303                     688.734                   631.411  
node-5.domain.tld              13.925                     682.965                   684.590  
node-5.domain.tld              15.720                     552.486                   649.983  
node-5.domain.tld              13.969                     728.804                   682.668  
node-5.domain.tld              14.665                     726.259                   626.595  
node-5.domain.tld              14.580                     625.517                   722.223  
=================  ==================  ==========================  ========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-5.domain.tld              16.703                     571.303                   639.126  
node-5.domain.tld              14.973                     607.173                   572.870  
node-5.domain.tld              17.503                     585.898                   566.977  
node-5.domain.tld              16.150                     549.462                   619.956  
node-5.domain.tld              15.089                     537.396                   595.933  
node-5.domain.tld              15.260                     582.331                   628.828  
node-5.domain.tld              17.858                     583.323                   589.186  
node-5.domain.tld              15.337                     631.261                   558.979  
=================  ==================  ==========================  ========================  

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download
    

.. image:: 3c1e6fe4-3104-4441-8e47-0df55c6f57a8.*

**Stats**:

===========  ==================  ==========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  
===========  ==================  ==========================  
          1               2.607                    3232.054  
          2               3.458                    3265.066  
          3               4.138                    2678.013  
          4               4.342                    2192.835  
          5               5.765                    1805.042  
          6               6.826                    1520.493  
          7               6.675                    1296.369  
          8               8.040                    1169.799  
===========  ==================  ==========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               2.607                    3232.054  
=================  ==================  ==========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               3.502                    3145.516  
node-5.domain.tld               3.414                    3384.616  
=================  ==================  ==========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               3.572                    2717.000  
node-5.domain.tld               4.748                    2564.076  
node-5.domain.tld               4.095                    2752.964  
=================  ==================  ==========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               3.553                    2268.765  
node-5.domain.tld               4.756                    2144.972  
node-5.domain.tld               4.268                    2252.282  
node-5.domain.tld               4.790                    2105.320  
=================  ==================  ==========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               6.567                    1742.666  
node-5.domain.tld               5.387                    1868.016  
node-5.domain.tld               6.395                    1952.902  
node-5.domain.tld               5.239                    1697.804  
node-5.domain.tld               5.238                    1763.824  
=================  ==================  ==========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               7.983                    1406.016  
node-5.domain.tld               7.363                    1513.164  
node-5.domain.tld               5.426                    1662.426  
node-5.domain.tld               6.578                    1646.744  
node-5.domain.tld               6.797                    1347.714  
node-5.domain.tld               6.809                    1546.890  
=================  ==================  ==========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               6.597                    1492.271  
node-5.domain.tld               7.262                    1109.728  
node-5.domain.tld               7.008                     965.674  
node-5.domain.tld               5.443                    1524.586  
node-5.domain.tld               6.323                     985.879  
node-5.domain.tld               7.445                    1444.538  
node-5.domain.tld               6.649                    1551.909  
=================  ==================  ==========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-5.domain.tld               9.141                    1218.768  
node-5.domain.tld               7.722                    1166.681  
node-5.domain.tld               7.881                    1041.818  
node-5.domain.tld               6.662                    1361.592  
node-5.domain.tld               6.829                    1189.834  
node-5.domain.tld               9.234                    1063.470  
node-5.domain.tld               8.444                    1263.239  
node-5.domain.tld               8.404                    1052.994  
=================  ==================  ==========================  

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload
    

.. image:: be794ce9-07e1-4ffa-bc60-ffba5e9673c2.*

**Stats**:

===========  ==================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_upload, Mbits/s  
===========  ==================  ========================  
          1               2.805                  3844.429  
          2               3.109                  3396.300  
          3               3.305                  2321.551  
          4               4.103                  2140.429  
          5               5.140                  1730.207  
          6               4.349                  1246.417  
          7               6.967                  1329.001  
          8               7.978                  1134.455  
===========  ==================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               2.805                  3844.429  
=================  ==================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               3.437                  3309.940  
node-5.domain.tld               2.781                  3482.660  
=================  ==================  ========================  

Concurrency 3
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               4.049                  1996.671  
node-5.domain.tld               2.798                  2942.325  
node-5.domain.tld               3.067                  2025.658  
=================  ==================  ========================  

Concurrency 4
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               3.823                  2223.731  
node-5.domain.tld               4.413                  2506.522  
node-5.domain.tld               3.682                  1833.083  
node-5.domain.tld               4.495                  1998.379  
=================  ==================  ========================  

Concurrency 5
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               4.086                  1527.113  
node-5.domain.tld               3.856                  1877.008  
node-5.domain.tld               7.207                  1451.293  
node-5.domain.tld               4.479                  1851.408  
node-5.domain.tld               6.072                  1944.213  
=================  ==================  ========================  

Concurrency 6
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               2.256                  2021.843  
node-5.domain.tld               3.417                   848.490  
node-5.domain.tld               1.590                   848.131  
node-5.domain.tld               1.259                   928.216  
node-5.domain.tld              14.412                   755.124  
node-5.domain.tld               3.160                  2076.700  
=================  ==================  ========================  

Concurrency 7
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               8.443                  1388.779  
node-5.domain.tld               5.399                  1497.742  
node-5.domain.tld               6.608                  1297.620  
node-5.domain.tld               6.731                  1210.056  
node-5.domain.tld               6.008                  1370.672  
node-5.domain.tld               8.472                  1330.812  
node-5.domain.tld               7.109                  1207.324  
=================  ==================  ========================  

Concurrency 8
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-5.domain.tld               8.757                  1131.878  
node-5.domain.tld               7.676                  1350.969  
node-5.domain.tld               7.685                  1058.382  
node-5.domain.tld               7.201                  1060.463  
node-5.domain.tld               6.972                   985.726  
node-5.domain.tld               9.804                  1117.549  
node-5.domain.tld               7.923                  1303.528  
node-5.domain.tld               7.805                  1067.145  
=================  ==================  ========================  

