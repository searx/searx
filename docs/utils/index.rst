
.. _searx_utils:
.. _toolboxing:

=======================
Tooling box ``utils/*``
=======================

In the folder :origin:`utils/` we maintain some tools useful for admins and
developers.

.. toctree::
   :maxdepth: 1

   searx.sh
   filtron.sh
   morty.sh

.. admonition:: Work needed!

   Our scripts to maintain services do most support only systemd init process
   used by debian, ubuntu and many other dists.  In general our scripts are only
   partially usable on debian systems.  We are working on this limitation, if
   you have any contribution, please send us your :pull:`PR <../pulls>`, see
   :ref:`how to contribute`.

.. _toolboxing common:

Common commands
===============

Scripts to maintain services often dispose of common commands and environments.

``shell``:
  Opens a shell from the service user ``${SERVICE_USSR}``, very helpful for
  troubleshooting.

``inspect service``:
  Shows status and log of the service, most often you have a option to enable
  more verbose debug logs.  Very helpful for debugging, but be careful not to
  enable debugging in a production environment!

.. _toolboxing setup:

Tooling box setup
=================

The main setup is done in the :origin:`.config.sh` (read also :ref:`makefile
setup`).

.. literalinclude:: ../../.config.sh
   :language: bash
