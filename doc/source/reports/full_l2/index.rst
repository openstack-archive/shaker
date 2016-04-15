.. _openstack_l2:

OpenStack L2
************

This scenario launches pairs of VMs in the same private network. Every VM is
hosted on a separate compute node.

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
    file_name: /home/ishakhat/Work/shaker/shaker/scenarios/openstack/full_l2.yaml
    title: OpenStack L2

Bi-directional
==============

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_bidirectional
    title: Bi-directional

.. image:: 722a69c0-c3e5-458c-99df-486484b1d481.*

**Stats**:

===========  ===================  =============  =====================
concurrency  tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
===========  ===================  =============  =====================
          1              3578.59           3.19                3547.75
          2              3912.17           2.95                3942.74
          5              3807.46           3.05                3791.78
         10              3752.25           2.89                3962.02
===========  ===================  =============  =====================

Concurrency 1
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-8.domain.tld              3578.59           3.19                3547.75
=================  ===================  =============  =====================

Concurrency 2
-------------

**Stats**:

=================  ===================  =============  =====================
node               tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
=================  ===================  =============  =====================
node-7.domain.tld              3680.14           3.21                3711.57
node-8.domain.tld              4144.20           2.68                4173.90
=================  ===================  =============  =====================

Concurrency 5
-------------

**Stats**:

==================  ===================  =============  =====================
node                tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
==================  ===================  =============  =====================
node-11.domain.tld              3551.67           3.33                3544.93
node-18.domain.tld              3795.47           3.04                3811.38
node-4.domain.tld               3898.52           3.00                3882.67
node-7.domain.tld               3970.07           2.82                4005.72
node-8.domain.tld               3821.60           3.04                3714.18
==================  ===================  =============  =====================

Concurrency 10
--------------

**Stats**:

==================  ===================  =============  =====================
node                tcp_upload, Mbits/s  ping_icmp, ms  tcp_download, Mbits/s
==================  ===================  =============  =====================
node-11.domain.tld              4014.04           2.85                3878.48
node-13.domain.tld              3767.26           3.24                3651.51
node-15.domain.tld              3316.62           2.96                3861.89
node-17.domain.tld              3330.25           2.88                4175.01
node-18.domain.tld              4208.58           2.74                3639.62
node-20.domain.tld              3988.34           2.74                4112.45
node-4.domain.tld               3939.45           3.08                4057.85
node-5.domain.tld               3846.78           3.01                3784.39
node-7.domain.tld               3390.47           2.38                4657.64
node-8.domain.tld               3720.68           2.98                3801.36
==================  ===================  =============  =====================

Download
========

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_download
    title: Download

.. image:: 193493d3-7de6-4f3e-976e-3bffc9f5776b.*

**Stats**:

===========  =============  =====================
concurrency  ping_icmp, ms  tcp_download, Mbits/s
===========  =============  =====================
          1           1.62                6758.58
          2           1.49                6747.02
          5           1.63                6755.12
         10           1.68                6615.10
===========  =============  =====================

Concurrency 1
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-8.domain.tld           1.62                6758.58
=================  =============  =====================

Concurrency 2
-------------

**Stats**:

=================  =============  =====================
node               ping_icmp, ms  tcp_download, Mbits/s
=================  =============  =====================
node-7.domain.tld           1.50                6771.23
node-8.domain.tld           1.47                6722.80
=================  =============  =====================

Concurrency 5
-------------

**Stats**:

==================  =============  =====================
node                ping_icmp, ms  tcp_download, Mbits/s
==================  =============  =====================
node-11.domain.tld           1.52                6650.81
node-18.domain.tld           1.70                6870.23
node-4.domain.tld            1.74                6688.20
node-7.domain.tld            1.57                6741.27
node-8.domain.tld            1.63                6825.11
==================  =============  =====================

Concurrency 10
--------------

**Stats**:

==================  =============  =====================
node                ping_icmp, ms  tcp_download, Mbits/s
==================  =============  =====================
node-11.domain.tld           1.43                6634.04
node-13.domain.tld           1.67                6769.58
node-15.domain.tld           1.60                6695.55
node-17.domain.tld           2.17                6145.54
node-18.domain.tld           1.64                6824.41
node-20.domain.tld           1.69                6786.08
node-4.domain.tld            1.70                6754.63
node-5.domain.tld            1.68                6572.60
node-7.domain.tld            1.80                6228.16
node-8.domain.tld            1.41                6740.39
==================  =============  =====================

Upload
======

**Test Specification**:

.. code-block:: yaml

    class: flent
    method: tcp_upload
    title: Upload

.. image:: 7220f722-0c40-4edb-a323-ab9d2df71e1b.*

**Stats**:

===========  ===================  =============
concurrency  tcp_upload, Mbits/s  ping_icmp, ms
===========  ===================  =============
          1              6804.07           1.43
          2              6784.08           1.62
          5              6671.28           1.69
         10              6692.88           1.64
===========  ===================  =============

Concurrency 1
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-8.domain.tld              6804.07           1.43
=================  ===================  =============

Concurrency 2
-------------

**Stats**:

=================  ===================  =============
node               tcp_upload, Mbits/s  ping_icmp, ms
=================  ===================  =============
node-7.domain.tld              6708.61           1.63
node-8.domain.tld              6859.54           1.61
=================  ===================  =============

Concurrency 5
-------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-11.domain.tld              6442.30           1.78
node-18.domain.tld              6514.95           1.47
node-4.domain.tld               7005.11           1.79
node-7.domain.tld               6682.03           1.58
node-8.domain.tld               6711.99           1.83
==================  ===================  =============

Concurrency 10
--------------

**Stats**:

==================  ===================  =============
node                tcp_upload, Mbits/s  ping_icmp, ms
==================  ===================  =============
node-11.domain.tld              6701.87           1.75
node-13.domain.tld              6777.32           1.64
node-15.domain.tld              6620.17           1.68
node-17.domain.tld              6469.74           1.52
node-18.domain.tld              6709.92           1.65
node-20.domain.tld              6686.77           1.62
node-4.domain.tld               6687.55           1.55
node-5.domain.tld               6896.79           1.62
node-7.domain.tld               6686.20           1.58
node-8.domain.tld               6692.50           1.75
==================  ===================  =============

