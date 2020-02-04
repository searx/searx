
.. _filtron.sh:

====================
``utils/filtron.sh``
====================

.. sidebar:: further reading

   - :ref:`installation`
   - :ref:`searx_filtron`
   - :ref:`architecture`

.. _Go: https://golang.org/
.. _filtron: https://github.com/asciimoo/filtron
.. _filtron README: https://github.com/asciimoo/filtron/blob/master/README.md

To simplify installation and maintenance of a filtron instance you can use the
script :origin:`utils/filtron.sh`.  In most cases you will install filtron_
simply by running the command:

.. code::  bash

   sudo -H ./utils/filtron.sh install all

The script adds a ``${SERVICE_USER}`` (default:``filtron``) and installs filtron_
into this user account:

#. Create a separated user account (``filtron``).
#. Download and install Go_ binary in users $HOME (``~filtron``).
#. Install filtron with the package management of Go_ (``go get -v -u
   github.com/asciimoo/filtron``)
#. Setup a proper rule configuration :origin:`[ref]
   <utils/templates/etc/filtron/rules.json>` (``/etc/filtron/rules.json``).
#. Setup a systemd service unit :origin:`[ref]
   <utils/templates/lib/systemd/system/filtron.service>`
   (``/lib/systemd/system/filtron.service``).

.. _reverse proxy:

Public Reverse Proxy
====================

To install searx in your public HTTP server use:

.. code::  bash

   sudo -H ./utils/filtron.sh apache install

.. tabs::

   .. group-tab:: apache

      .. literalinclude:: ../../utils/templates/etc/apache2/sites-available/searx.conf:filtron
	 :language: apache

      .. tabs::

	 .. group-tab:: Ubuntu / debian

	       .. code-block:: sh

		  $ sudo -H a2enmod headers
		  $ sudo -H a2enmod proxy
		  $ sudo -H a2enmod proxy_http


Overview
========

The ``--help`` output of the script is largely self-explanatory
(:ref:`toolboxing common`):

.. program-output:: ../utils/filtron.sh --help

