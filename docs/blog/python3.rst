Introducing Python3 support
===========================

As most operation systems are coming with Python3 installed by default. So it is time for searx to support Python3. But don't worry support of Python2.7 won't be dropped.

.. image:: searxpy3.png
    :scale: 50 %
    :alt: hurray
    :align: center


How to run searx using Python3
------------------------------

Please make sure that you run at least Python3.5.

To run searx, first a Python3 virtualenv should be created. After entering the virtualenv,
dependencies must be installed. Then run searx with python3 instead of the usual python command.

.. code:: sh

    virtualenv -p python3 venv3
    source venv3/bin/activate
    pip3 install -r requirements.txt
    python3 searx/webapp.py


If you want to run searx using Python2.7, you don't have to do anything differently as before.

Fun facts
---------

- 115 files were changed when implementing the support for both Python versions.

- All of the dependencies was compatible except for the robotframework used for browser tests. Thus, these tests were migrated to splinter. So from now on both versions are being tested on Travis and can be tested locally.

If you found bugs...
--------------------

...please open an issue on `GitHub`_. Make sure that you mention your Python version in your issue,
so we can investigate it properly.

.. _GitHub: https://github.com/asciimoo/searx/issues

Acknowledgement
---------------

This development was sponsored by `NLnet Foundation`_.

.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2017.05.13 22:57
