
.. _morty.sh:

.. _morty: https://github.com/asciimoo/morty
.. _morty's README: https://github.com/asciimoo/morty

==================
``utils/morty.sh``
==================

To simplify installation and maintenance of a morty_ instance you can use the
script :origin:`utils/morty.sh`.  In most cases you will install morty_ simply by
running the command:

.. code::  bash

   sudo -H ./utils/morty.sh install all

The script adds a ``${SERVICE_USER}`` (default:``morty``) and installs morty_
into this user account.

.. hint::

   To add morty to your searx instance read chapter :reF:`searx_morty`.


The ``--help`` output of the script is largely
self-explanatory:

.. program-output:: ../utils/morty.sh --help

