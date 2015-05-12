============
Installation
============

Shaker is distributed as Python package and available through PyPi (https://pypi.python.org/pypi/pyshaker/).
It is recommended to be installed inside virtualenv.

.. code::

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install pyshaker


Installation on Ubuntu Cloud Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code::

    $ sudo apt-add-repository "deb http://nova.clouds.archive.ubuntu.com/ubuntu/ trusty multiverse"
    $ sudo apt-get update
    $ sudo apt-get -y install python-dev libzmq-dev
    $ wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py
    $ sudo pip install pbr pyshaker
    $ shaker --help


Installation on MacOSX
^^^^^^^^^^^^^^^^^^^^^^

Shaker can run natively on MacOSX, however it is recommended to use brewed python

.. code::

    $ wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py
    $ sudo pip install pbr pyshaker
    $ shaker --help
