
.. _searx.sh:

==================
``utils/searx.sh``
==================

To simplify installation and maintenance of a searx instance you can use the
script :origin:`utils/searx.sh`.  In most cases you will install searx simply by
running the command:

.. code::  bash

   sudo -H ./utils/searx.sh install all

The script adds a ``${SERVICE_USER}`` (default:``searx``) and installs searx
into this user account.  The ``--help`` output of the script is largely
self-explanatory:

.. program-output:: ../utils/searx.sh --help

