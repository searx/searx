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

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START distro-packages
   :end-before: END distro-packages

.. hint::

   This installs also the packages needed by :ref:`searx uwsgi`

.. _create searx user:

Create user
===========

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START create user
   :end-before: END create user

.. _searx-src:

install searx & dependencies
============================

Start a interactive shell from new created user and clone searx:

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START clone searx
   :end-before: END clone searx

In the same shell create *virtualenv*:

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START create virtualenv
   :end-before: END create virtualenv

To install searx's dependencies, exit the searx *bash* session you opened above
and restart a new.  Before install, first check if your *virualenv* was sourced
from the login (*~/.profile*):

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START manage.sh update_packages
   :end-before: END manage.sh update_packages

.. tip::

   Open a second terminal for the configuration tasks and left the ``(searx)$``
   terminal open for the tasks below.

Configuration
==============

Create a copy of the :origin:`searx/settings.yml` configuration file in system's
*/etc* folder.  Configure like shown below -- replace ``searx@\$(uname -n)`` with
a name of your choice -- *and/or* edit ``/etc/searx/settings.yml`` if necessary.

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START searx config
   :end-before: END searx config

Check
=====

To check your searx setup, optional enable debugging and start the *webapp*.
Searx looks at the exported environment ``$SEARX_SETTINGS_PATH`` for a
configuration file.

.. include:: ../../build/docs/includes/searx.rst
   :start-after: START check searx installation
   :end-before: END check searx installation

If everything works fine, hit ``[CTRL-C]`` to stop the *webapp* and disable the
debug option in ``settings.yml``. You can now exit searx user bash (enter exit
command twice).  At this point searx is not demonized; uwsgi allows this.

