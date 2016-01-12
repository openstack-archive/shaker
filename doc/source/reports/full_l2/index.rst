.. _openstack_l2:

OpenStack L2
************

This scenario launches pairs of VMs in the same private network. Every VM is hosted on a separate compute node.

**Scenario**:

.. code-block:: yaml

    deployment:
      accommodation:
      - pair
      - single_room
      template: l2.hot
    description: This scenario launches pairs of VMs in the same private network. Every
      VM is hosted on a separate compute node.
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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/networking/full_l2.yaml
    title: OpenStack L2
    

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional
    

.. image:: ad4d8574-e509-46d1-923a-23992fde612a.*

**Stats**:

===========  ==================  ==========================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
===========  ==================  ==========================  ========================  
          1               3.194                    3547.748                  3578.587  
          2               2.948                    3942.737                  3912.168  
          5               3.049                    3791.777                  3807.464  
         10               2.886                    3962.019                  3752.248  
===========  ==================  ==========================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-8.domain.tld               3.194                    3547.748                  3578.587  
=================  ==================  ==========================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  ========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
=================  ==================  ==========================  ========================  
node-7.domain.tld               3.213                    3711.573                  3680.139  
node-8.domain.tld               2.684                    4173.901                  4144.196  
=================  ==================  ==========================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-11.domain.tld               3.331                    3544.930                  3551.672  
node-18.domain.tld               3.044                    3811.383                  3795.467  
node-4.domain.tld                3.004                    3882.672                  3898.517  
node-7.domain.tld                2.822                    4005.723                  3970.065  
node-8.domain.tld                3.043                    3714.178                  3821.601  
==================  ==================  ==========================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  ========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  mean tcp_upload, Mbits/s  
==================  ==================  ==========================  ========================  
node-11.domain.tld               2.851                    3878.477                  4014.036  
node-13.domain.tld               3.236                    3651.506                  3767.255  
node-15.domain.tld               2.962                    3861.893                  3316.622  
node-17.domain.tld               2.881                    4175.013                  3330.247  
node-18.domain.tld               2.738                    3639.621                  4208.584  
node-20.domain.tld               2.744                    4112.447                  3988.342  
node-4.domain.tld                3.081                    4057.848                  3939.452  
node-5.domain.tld                3.009                    3784.387                  3846.785  
node-7.domain.tld                2.376                    4657.638                  3390.474  
node-8.domain.tld                2.980                    3801.357                  3720.680  
==================  ==================  ==========================  ========================  

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download
    

.. image:: dd111bc5-c2c0-44bf-a748-b2bd671d3744.*

**Stats**:

===========  ==================  ==========================  
concurrency  mean ping_icmp, ms  mean tcp_download, Mbits/s  
===========  ==================  ==========================  
          1               1.622                    6758.582  
          2               1.488                    6747.016  
          5               1.630                    6755.124  
         10               1.678                    6615.098  
===========  ==================  ==========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-8.domain.tld               1.622                    6758.582  
=================  ==================  ==========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ==========================  
node               mean ping_icmp, ms  mean tcp_download, Mbits/s  
=================  ==================  ==========================  
node-7.domain.tld               1.504                    6771.228  
node-8.domain.tld               1.472                    6722.804  
=================  ==================  ==========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-11.domain.tld               1.521                    6650.814  
node-18.domain.tld               1.696                    6870.225  
node-4.domain.tld                1.736                    6688.205  
node-7.domain.tld                1.568                    6741.267  
node-8.domain.tld                1.631                    6825.110  
==================  ==================  ==========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ==========================  
node                mean ping_icmp, ms  mean tcp_download, Mbits/s  
==================  ==================  ==========================  
node-11.domain.tld               1.429                    6634.041  
node-13.domain.tld               1.674                    6769.581  
node-15.domain.tld               1.596                    6695.549  
node-17.domain.tld               2.167                    6145.539  
node-18.domain.tld               1.636                    6824.412  
node-20.domain.tld               1.692                    6786.083  
node-4.domain.tld                1.698                    6754.628  
node-5.domain.tld                1.680                    6572.598  
node-7.domain.tld                1.797                    6228.162  
node-8.domain.tld                1.406                    6740.390  
==================  ==================  ==========================  

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload
    

.. image:: f5abeef1-0b5e-48d3-9fa2-6dd52faa833f.*

**Stats**:

===========  ==================  ========================  
concurrency  mean ping_icmp, ms  mean tcp_upload, Mbits/s  
===========  ==================  ========================  
          1               1.429                  6804.068  
          2               1.620                  6784.078  
          5               1.690                  6671.276  
         10               1.637                  6692.882  
===========  ==================  ========================  

Concurrency 1
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-8.domain.tld               1.429                  6804.068  
=================  ==================  ========================  

Concurrency 2
-------------

**Stats**:

=================  ==================  ========================  
node               mean ping_icmp, ms  mean tcp_upload, Mbits/s  
=================  ==================  ========================  
node-7.domain.tld               1.634                  6708.612  
node-8.domain.tld               1.606                  6859.543  
=================  ==================  ========================  

Concurrency 5
-------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-11.domain.tld               1.779                  6442.300  
node-18.domain.tld               1.469                  6514.949  
node-4.domain.tld                1.787                  7005.110  
node-7.domain.tld                1.585                  6682.033  
node-8.domain.tld                1.830                  6711.989  
==================  ==================  ========================  

Concurrency 10
--------------

**Stats**:

==================  ==================  ========================  
node                mean ping_icmp, ms  mean tcp_upload, Mbits/s  
==================  ==================  ========================  
node-11.domain.tld               1.747                  6701.867  
node-13.domain.tld               1.643                  6777.320  
node-15.domain.tld               1.683                  6620.175  
node-17.domain.tld               1.523                  6469.738  
node-18.domain.tld               1.652                  6709.921  
node-20.domain.tld               1.620                  6686.766  
node-4.domain.tld                1.552                  6687.551  
node-5.domain.tld                1.621                  6896.787  
node-7.domain.tld                1.583                  6686.195  
node-8.domain.tld                1.747                  6692.503  
==================  ==================  ========================  

