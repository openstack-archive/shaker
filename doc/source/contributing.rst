============
Contributing
============

Contribute to Shaker
--------------------

Shaker follows standard OpenStack contribution workflow as described at http://docs.openstack.org/infra/manual/developers.html


Start working
^^^^^^^^^^^^^

1. Clone the repo::

    $ git clone git://git.openstack.org/openstack/shaker

2. From the root of your workspace, check out a new branch to work on::

    $ git checkout -b <TOPIC-BRANCH>

3. Implement your code


Before Commit
^^^^^^^^^^^^^

4. Make sure your code works by running the tests::

    $ tox

By default tox executes the same set of tests as configured in Jenkins, i.e.: py34 and py27 unit tests,
pep8 style check and documentation build.

5. If there are any changes in config parameters, also do::

    $ tox -egenconfig

This job updates sample config file as well as documentation on CLI utils.


Submit Review
^^^^^^^^^^^^^

6. Commit the code::

    $ git commit -a

Commit message should indicate what the change is, for a bug fix commit it needs to contain reference to Launchpad bug number.

7. Submit the review::

    $ git review

8. If the code is approved with a +2 review, Gerrit will automatically merge your code.


Bug Tracking
------------

Bugs are tracked at Launchpad:

   https://bugs.launchpad.net/shaker


Developer's Guide of OpenStack
------------------------------

If you would like to contribute to the development of OpenStack, you must follow the steps in this page:

   http://docs.openstack.org/infra/manual/developers.html

Once those steps have been completed, changes to OpenStack should be submitted for review via the Gerrit tool, following the workflow documented at:

   http://docs.openstack.org/infra/manual/developers.html#development-workflow

Pull requests submitted through GitHub will be ignored.

