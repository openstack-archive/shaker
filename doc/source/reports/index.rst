Reports
=======

All reports under this folder are collected in the following environment:
 * 20 bare-metal nodes running KVM
 * 10Gb tenant network
 * 1Gb floating network
 * Neutron ML2 plugin with VXLAN
 * Neutron HA routers

To generate the report based on raw data:

    .. code::

        shaker-report --input <raw data> --book <folder to store book into>

.. toctree::
    :maxdepth: 2

    full_l2/index
    full_l3_east_west/index
    full_l3_north_south/index
    perf_l2/index
    perf_l3_east_west/index
    perf_l3_north_south/index
    dense_l2/index
    dense_l3_east_west/index
