.. _devquickstart:

======================
Development Quickstart
======================

.. sidebar:: :ref:`makefile`

   For additional developer purpose there are :ref:`makefile`.

This quickstart guide gets your environment set up with searx.  Furthermore, it
gives a short introduction to the ``manage.sh`` script.

How to setup your development environment
=========================================

.. sidebar:: :ref:`make pyenv <make pyenv>`

   Alternatively use the :ref:`make pyenv`.

First, clone the source code of searx to the desired folder.  In this case the
source is cloned to ``~/myprojects/searx``.  Then create and activate the
searx-ve virtualenv and install the required packages using ``manage.sh``.

.. code:: sh

    cd ~/myprojects
    git clone https://github.com/asciimoo/searx.git
    cd searx
    virtualenv searx-ve
    . ./searx-ve/bin/activate
    ./manage.sh update_dev_packages


How to run tests
================

.. sidebar:: :ref:`make test.unit <make test>`

   Alternatively use the ``test.pep8``, ``test.unit``, ``test.robot`` targets.

Tests can be run using the ``manage.sh`` script.  Following tests and checks are
available:

- Unit tests
- Selenium tests
- PEP8 validation
- Unit test coverage check

For example unit tests are run with the command below:

.. code:: sh

   ./manage.sh unit_tests

For further test options, please consult the help of the ``manage.sh`` script or
read :ref:`make test`.


How to compile styles and javascript
====================================

.. _less: http://lesscss.org/
.. _NodeJS: https://nodejs.org

How to build styles
-------------------

Less_ is required to build the styles of searx.  Less_ can be installed using
either NodeJS_ or Apt.

.. code:: sh

   sudo -H apt-get install nodejs
   sudo -H npm install -g less

OR

.. code:: sh

   sudo -H apt-get install node-less

After satisfying the requirements styles can be build using ``manage.sh``

.. code:: sh

   ./manage.sh styles


How to build the source of the themes
=====================================

.. _grunt: https://gruntjs.com/

Grunt_ must be installed in order to build the javascript sources. It depends on
NodeJS, so first Node has to be installed.

.. code:: sh

   sudo -H apt-get install nodejs
   make node.env

After installing grunt, the files can be built using the following command:

.. code:: sh

   make themes


Tips for debugging/development
==============================

.. sidebar:: :ref:`make run`

   Makefile target ``run`` already enables debug option for your developer
   session / see :ref:`make run`.

Turn on debug logging
  Whether you are working on a new engine or trying to eliminate a bug, it is
  always a good idea to turn on debug logging.  When debug logging is enabled a
  stack trace appears, instead of the cryptic ``Internal Server Error``
  message. It can be turned on by setting ``debug: False`` to ``debug: True`` in
  :origin:`settings.yml <searx/settings.yml>`.

.. sidebar:: :ref:`make test`

   Alternatively use the :ref:`make test` targets.

Run ``./manage.sh tests`` before creating a PR.
  Failing build on Travis is common because of PEP8 checks.  So a new commit
  must be created containing these format fixes.  This phase can be skipped if
  ``./manage.sh tests`` is run locally before creating a PR.
