
.. _searx.sh:

==================
``utils/searx.sh``
==================

.. sidebar:: further reading

   - :ref:`installation`
   - :ref:`architecture`

To simplify installation and maintenance of a searx instance you can use the
script :origin:`utils/searx.sh`.  In most cases you will install searx simply by
running the command:

.. code::  bash

   sudo -H ./utils/searx.sh install all

The script adds a ``${SERVICE_USER}`` (default:``searx``) and installs searx
into this user account.  The installation is described in chapter
:ref:`installation basic`.

.. _intranet reverse proxy:

Intranet Reverse Proxy
======================

.. warning::

   This setup is **not** suitable **for public instances**, go on with
   :ref:`reverse proxy`!

To install searx in your intranet HTTP server use:

.. code::  bash

   sudo -H ./utils/searx.sh apache install

.. tabs::

   .. group-tab:: apache

      .. literalinclude:: ../../utils/templates/etc/apache2/sites-available/searx.conf:uwsgi
	 :language: apache

      .. tabs::

	 .. group-tab:: Ubuntu / debian

	       .. code-block:: sh

		  $ sudo -H apt install libapache2-mod-uwsgi

	 .. group-tab:: Arch Linux

	    .. code-block:: sh

	       $ sudo pacman -S uwsgi

Overview
========

The ``--help`` output of the script is largely self-explanatory
(:ref:`toolboxing common`):

.. program-output:: ../utils/searx.sh --help
