============================
Introducing Python 3 support
============================

.. _Python 2.7 clock: https://pythonclock.org/

.. sidebar:: Python 2.7 to 3 upgrade

   This chapter exists of historical reasons.  Python 2.7 release schedule ends
   (`Python 2.7 clock`_) after 11 years Python 3 exists

As most operation systems are coming with Python3 installed by default. So it is
time for searx to support Python3.  But don't worry support of Python2.7 won't be
dropped.

.. image:: searxpy3.png
    :scale: 50 %
    :alt: hurray
    :align: center


How to run searx using Python 3
===============================

Please make sure that you run at least Python 3.5.

To run searx, first a Python3 virtualenv should be created.  After entering the
virtualenv, dependencies and searx must be installed. Then run searx from the
command line.

.. code:: sh

    python3 -m venv venv3
    source venv3/bin/activate
    pip install -U pip setuptools wheel pyyaml
    pip install -e .
    searx-run

Fun facts
=========

- 115 files were changed when implementing the support for both Python versions.

- All of the dependencies was compatible except for the robotframework used for
  browser tests.  Thus, these tests were migrated to splinter. So from now on
  both versions are being tested on Travis and can be tested locally.

If you found bugs
=================

Please open an issue on `GitHub`_.  Make sure that you mention your Python
version in your issue, so we can investigate it properly.

.. _GitHub: https://github.com/searxng/searxng/issues

Acknowledgment
==============

This development was sponsored by `NLnet Foundation`_.

.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2017.05.13 22:57
