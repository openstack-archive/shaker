.. _openstack_l3_east_west:

OpenStack L3 East-West
**********************

This scenario launches pairs of VMs in different networks connected to one router (L3 east-west)

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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/networking/full_l3_east_west.yaml
    title: OpenStack L3 East-West
    

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional
    

.. image:: 46dff27b-f0ae-421c-939f-9d5a112f0c1a.*

**Stats**:

===========  ==================  ==========================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
===========  ==================  ==========================  ========================  
          1               2.920                    3816.623                  3474.929  
          2               4.876                    2264.434                  2632.596  
          5               7.106                    1016.467                   991.037  
         10               9.541                     491.522                   514.838  
===========  ==================  ==========================  ========================  

Concurrency 1
-------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-13.domain.tld               2.920                    3816.623                  3474.929  
==================  ==================  ==========================  ========================  

Concurrency 2
-------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-13.domain.tld               6.556                    2423.299                  2639.193  
node-15.domain.tld               3.195                    2105.569                  2625.999  
==================  ==================  ==========================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-13.domain.tld              10.073                     971.692                   839.748  
node-15.domain.tld               6.335                    1490.886                   948.819  
node-20.domain.tld               5.691                     758.929                   889.136  
node-4.domain.tld                7.685                     786.010                  1125.130  
node-5.domain.tld                5.747                    1074.818                  1152.351  
==================  ==================  ==========================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-11.domain.tld               9.515                     752.079                   763.627  
node-13.domain.tld              13.497                     320.141                   935.469  
node-15.domain.tld               5.848                     354.125                   506.368  
node-17.domain.tld              13.271                     902.346                   346.841  
node-18.domain.tld              13.416                     790.133                   358.234  
node-20.domain.tld               5.989                     378.521                   360.619  
node-4.domain.tld                9.378                     346.472                   437.557  
node-5.domain.tld                5.701                     367.271                   706.908  
node-7.domain.tld                9.465                     347.718                   392.195  
node-8.domain.tld                9.329                     356.415                   340.560  
==================  ==================  ==========================  ========================  

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download
    

.. image:: 222ee609-db4e-45e5-9dba-89994b5e1908.*

**Stats**:

===========  ==================  ==========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  
===========  ==================  ==========================  
          1               0.960                    4049.222  
          2               2.092                    4792.047  
          5               3.937                    1858.962  
         10               7.617                     999.793  
===========  ==================  ==========================  

Concurrency 1
-------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-13.domain.tld               0.960                    4049.222  
==================  ==================  ==========================  

Concurrency 2
-------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-13.domain.tld               2.807                    5126.855  
node-15.domain.tld               1.377                    4457.238  
==================  ==================  ==========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-13.domain.tld               4.332                    1475.563  
node-15.domain.tld               7.912                    1486.695  
node-20.domain.tld               2.154                    2385.874  
node-4.domain.tld                3.867                    2470.585  
node-5.domain.tld                1.419                    1476.096  
==================  ==================  ==========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-11.domain.tld               7.676                     842.155  
node-13.domain.tld               8.502                    1180.856  
node-15.domain.tld               6.763                    1496.945  
node-17.domain.tld               8.799                    1018.096  
node-18.domain.tld               8.775                     979.223  
node-20.domain.tld               6.474                     893.750  
node-4.domain.tld                7.520                     846.167  
node-5.domain.tld                6.592                     822.034  
node-7.domain.tld                7.422                     866.793  
node-8.domain.tld                7.645                    1051.914  
==================  ==================  ==========================  

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload
    

.. image:: b30e8cc2-12b0-4756-985f-adfe758b1afb.*

**Stats**:

===========  ==================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_upload, Mbits/s  
===========  ==================  ========================  
          1               0.786                  4209.986  
          2               2.981                  3849.737  
          5               5.475                  1996.737  
         10               8.047                  1009.214  
===========  ==================  ========================  

Concurrency 1
-------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-13.domain.tld               0.786                  4209.986  
==================  ==================  ========================  

Concurrency 2
-------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-13.domain.tld               2.075                  4086.936  
node-15.domain.tld               3.888                  3612.538  
==================  ==================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-13.domain.tld               9.046                  2053.603  
node-15.domain.tld               3.706                  1525.483  
node-20.domain.tld               3.937                  1463.324  
node-4.domain.tld                6.730                  3485.968  
node-5.domain.tld                3.956                  1455.309  
==================  ==================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-11.domain.tld               8.193                   830.319  
node-13.domain.tld              11.137                   720.020  
node-15.domain.tld               4.958                   807.430  
node-17.domain.tld              11.023                   956.327  
node-18.domain.tld              11.209                   926.504  
node-20.domain.tld               5.038                  1272.343  
node-4.domain.tld                8.074                  1371.940  
node-5.domain.tld                4.912                  1306.218  
node-7.domain.tld                7.853                   906.627  
node-8.domain.tld                8.078                   994.410  
==================  ==================  ========================  

