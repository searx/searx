
.. _morty: https://github.com/asciimoo/morty
.. _morty's README: https://github.com/asciimoo/morty
.. _Go: https://golang.org/

.. _morty.sh:

==================
``utils/morty.sh``
==================

.. sidebar:: further reading

   - :ref:`installation`
   - :ref:`architecture`

To simplify installation and maintenance of a morty_ instance you can use the
script :origin:`utils/morty.sh`.  In most cases you will install morty_ simply by
running the command:

.. code::  bash

   sudo -H ./utils/morty.sh install all

The script adds a ``${SERVICE_USER}`` (default:``morty``) and installs morty_
into this user account:

#. Create a separated user account (``morty``).
#. Download and install Go_ binary in user's $HOME (``~morty``).
#. Install morty_ with the package management from Go_ (``go get -v -u
   github.com/asciimoo/morty``)
#. Setup a systemd service unit :origin:`[ref]
   <utils/templates/lib/systemd/system/morty.service>`
   (``/lib/systemd/system/morty.service``).

.. hint::

   To add morty to your searx instance read chapter :ref:`searx morty`.


Overview
========

The ``--help`` output of the script is largely self-explanatory
(:ref:`toolboxing common`):

.. program-output:: ../utils/morty.sh --help

