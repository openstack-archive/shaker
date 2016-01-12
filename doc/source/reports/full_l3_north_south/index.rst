.. _openstack_l3_north_south:

OpenStack L3 North-South
************************

This scenario launches pairs of VMs on different compute nodes. VMs are in the different networks connected via different routers, master accesses slave by floating ip

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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/networking/full_l3_north_south.yaml
    title: OpenStack L3 North-South
    

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional
    

.. image:: 09daaf80-77af-4b06-80b5-2f47a14f7ac9.*

**Stats**:

===========  ==================  ==========================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
===========  ==================  ==========================  ========================  
          1               2.825                     677.492                   730.017  
          2               1.104                     458.308                   464.958  
          5              19.691                     186.562                   188.006  
         10              52.703                      93.525                    95.158  
===========  ==================  ==========================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-7.domain.tld               2.825                     677.492                   730.017  
=================  ==================  ==========================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-7.domain.tld               1.167                     463.710                   358.626  
node-8.domain.tld               1.042                     452.906                   571.289  
=================  ==================  ==========================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-17.domain.tld               1.174                     131.380                   126.002  
node-18.domain.tld              23.304                     174.599                   248.758  
node-4.domain.tld               48.845                     218.449                   174.126  
node-7.domain.tld                1.248                     252.505                   247.466  
node-8.domain.tld               23.883                     155.875                   143.678  
==================  ==================  ==========================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-11.domain.tld              32.099                      70.717                   105.893  
node-13.domain.tld              58.906                      41.090                    87.657  
node-15.domain.tld              49.674                      50.966                    66.216  
node-17.domain.tld              49.532                     134.962                   107.459  
node-18.domain.tld              57.204                     195.383                    73.912  
node-20.domain.tld              64.021                      47.331                   109.201  
node-4.domain.tld               69.011                      93.190                   130.025  
node-5.domain.tld               36.935                     160.036                    84.940  
node-7.domain.tld               50.129                      80.142                    53.355  
node-8.domain.tld               59.518                      61.436                   132.917  
==================  ==================  ==========================  ========================  

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download
    

.. image:: 9a38034e-7776-4a3c-b918-6fa53aca0476.*

**Stats**:

===========  ==================  ==========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  
===========  ==================  ==========================  
          1               1.382                     922.297  
          2               1.012                     475.849  
          5              33.933                     191.923  
         10              47.527                      97.229  
===========  ==================  ==========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-7.domain.tld               1.382                     922.297  
=================  ==================  ==========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-7.domain.tld               1.117                     472.463  
node-8.domain.tld               0.908                     479.234  
=================  ==================  ==========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-17.domain.tld              39.776                     192.507  
node-18.domain.tld              41.846                     189.755  
node-4.domain.tld               45.339                     189.535  
node-7.domain.tld               41.662                     189.807  
node-8.domain.tld                1.040                     198.012  
==================  ==================  ==========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-11.domain.tld              50.274                     161.816  
node-13.domain.tld              51.326                      66.993  
node-15.domain.tld              54.017                      83.388  
node-17.domain.tld              54.224                      62.380  
node-18.domain.tld              54.203                      77.166  
node-20.domain.tld              54.217                      51.602  
node-4.domain.tld               50.462                      97.858  
node-5.domain.tld                0.984                      53.753  
node-7.domain.tld               54.302                     158.173  
node-8.domain.tld               51.259                     159.158  
==================  ==================  ==========================  

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload
    

.. image:: a2ae5461-c5cb-4c27-814f-e1a8d0f1cc72.*

**Stats**:

===========  ==================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_upload, Mbits/s  
===========  ==================  ========================  
          1               0.863                   890.059  
          2               8.439                   481.631  
          5              31.442                   190.862  
         10              61.755                    97.726  
===========  ==================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-7.domain.tld               0.863                   890.059  
=================  ==================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-7.domain.tld               0.748                   476.546  
node-8.domain.tld              16.130                   486.717  
=================  ==================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-17.domain.tld              41.426                   192.284  
node-18.domain.tld               0.869                   190.411  
node-4.domain.tld               38.764                   189.013  
node-7.domain.tld               36.400                   190.015  
node-8.domain.tld               39.748                   192.588  
==================  ==================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-11.domain.tld              62.149                   138.338  
node-13.domain.tld              64.569                   138.369  
node-15.domain.tld              63.771                    63.266  
node-17.domain.tld              63.557                    72.492  
node-18.domain.tld              58.727                   137.215  
node-20.domain.tld              64.664                    56.734  
node-4.domain.tld               60.727                    76.946  
node-5.domain.tld               59.091                    68.550  
node-7.domain.tld               59.114                    87.670  
node-8.domain.tld               61.180                   137.680  
==================  ==================  ========================  

