
.. _morty: https://github.com/asciimoo/morty
.. _morty's README: https://github.com/asciimoo/morty

.. _morty.sh:

==================
``utils/morty.sh``
==================

.. sidebar:: further reading

   - :ref:`architecture`

To simplify installation and maintenance of a morty_ instance you can use the
script :origin:`utils/morty.sh`.  In most cases you will install morty_ simply by
running the command:

.. code::  bash

   sudo -H ./utils/morty.sh install all

The script adds a ``${SERVICE_USER}`` (default:``morty``) and installs morty_
into this user account.

.. hint::

   To add morty to your searx instance read chapter :reF:`searx_morty`.


Overview
========

The ``--help`` output of the script is largely self-explanatory
(:ref:`toolboxing common`):

.. program-output:: ../utils/morty.sh --help

