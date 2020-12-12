.. _installation basic:

=========================
Step by step installation
=========================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

Step by step installation with virtualenv.  For Ubuntu, be sure to have enable
universe repository.

.. _install packages:

Install packages
================

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START distro-packages
   :end-before: END distro-packages

.. hint::

   This installs also the packages needed by :ref:`searx uwsgi`

.. _create searx user:

Create user
===========

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START create user
   :end-before: END create user

.. _searx-src:

install searx & dependencies
============================

Start a interactive shell from new created user and clone searx:

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START clone searx
   :end-before: END clone searx

In the same shell create *virtualenv*:

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START create virtualenv
   :end-before: END create virtualenv

To install searx's dependencies, exit the searx *bash* session you opened above
and restart a new.  Before install, first check if your *virtualenv* was sourced
from the login (*~/.profile*):

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START manage.sh update_packages
   :end-before: END manage.sh update_packages

.. tip::

   Open a second terminal for the configuration tasks and left the ``(searx)$``
   terminal open for the tasks below.


.. _use_default_settings.yml:

Configuration
=============

To create a initial ``/etc/searx/settings.yml`` you can start with a copy of the
file :origin:`utils/templates/etc/searx/use_default_settings.yml`.  This setup
:option:ref:`use default settings <settings use_default_settings>` from
:origin:`searx/settings.yml` and is recommended since :pull:`2291` is merged.

For minimal Setup, configure like shown below – replace ``searx@\$(uname -n)``
with a name of your choice, set ``ultrasecretkey`` -- *and/or* edit
``/etc/searx/settings.yml`` to your needs.

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START searx config
   :end-before: END searx config

.. tabs::

  .. group-tab:: Use default settings

    .. literalinclude:: ../../utils/templates/etc/searx/use_default_settings.yml
       :language: yaml

  .. group-tab:: searx/settings.yml

    .. literalinclude:: ../../searx/settings.yml
       :language: yaml


Check
=====

To check your searx setup, optional enable debugging and start the *webapp*.
Searx looks at the exported environment ``$SEARX_SETTINGS_PATH`` for a
configuration file.

.. kernel-include:: $DOCS_BUILD/includes/searx.rst
   :start-after: START check searx installation
   :end-before: END check searx installation

If everything works fine, hit ``[CTRL-C]`` to stop the *webapp* and disable the
debug option in ``settings.yml``. You can now exit searx user bash (enter exit
command twice).  At this point searx is not demonized; uwsgi allows this.

