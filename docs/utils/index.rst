.. _searx_utils:
.. _toolboxing:

=======================
Tooling box ``utils/*``
=======================

In the folder :origin:`utils/` we maintain some tools useful for admins and
developers.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   searx.sh
   filtron.sh
   morty.sh
   lxc.sh

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
