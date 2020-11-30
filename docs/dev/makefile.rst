.. _makefile:

================
Makefile Targets
================

.. _gnu-make: https://www.gnu.org/software/make/manual/make.html#Introduction

.. sidebar:: build environment

   Before looking deeper at the targets, first read about :ref:`makefile setup`
   and :ref:`make pyenv`.

   To install system requirements follow :ref:`buildhosts`.

With the aim to simplify development cycles, started with :pull:`1756` a
``Makefile`` based boilerplate was added.  If you are not familiar with
Makefiles, we recommend to read gnu-make_ introduction.

The usage is simple, just type ``make {target-name}`` to *build* a target.
Calling the ``help`` target gives a first overview (``make help``):

.. program-output:: bash -c "cd ..; make --no-print-directory help"


.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry


.. _makefile setup:

Makefile setup
==============

.. _git stash: https://git-scm.com/docs/git-stash

.. sidebar:: fork & upstream

   Commit changes in your (local) branch, fork or whatever, but do not push them
   upstream / `git stash`_ is your friend.

The main setup is done in the :origin:`Makefile`.

.. literalinclude:: ../../Makefile
   :start-after: START Makefile setup
   :end-before: END Makefile setup

:GIT_URL:    Changes this, to point to your searx fork.
:GIT_BRANCH: Changes this, to point to your searx branch.
:SEARX_URL:  Changes this, to point to your searx instance.
:DOCS_URL:   If you host your own (*brand*) documentation, change this URL.

If you change any of this build environment variables, you have to run ``make
buildenv``::

  $ make buildenv
  build searx/brand.py
  build utils/brand.env

.. _make pyenv:

Python environment
==================

.. sidebar:: activate environment

   ``source ./local/py3/bin/activate``

With Makefile we do no longer need to build up the virtualenv manually (as
described in the :ref:`devquickstart` guide).  Jump into your git working tree
and release a ``make pyenv``:

.. code:: sh

   $ cd ~/searx-clone
   $ make pyenv
   PYENV     usage: source ./local/py3/bin/activate
   ...

With target ``pyenv`` a development environment (aka virtualenv) was build up in
``./local/py3/``.  To make a *developer install* of searx (:origin:`setup.py`)
into this environment, use make target ``install``:

.. code:: sh

   $ make install
   PYENV     usage: source ./local/py3/bin/activate
   PYENV     using virtualenv from ./local/py3
   PYENV     install .

You have never to think about intermediate targets like ``pyenv`` or
``install``, the ``Makefile`` chains them as requisites.  Just run your main
target.

.. sidebar:: drop environment

   To get rid of the existing environment before re-build use :ref:`clean target
   <make clean>` first.

If you think, something goes wrong with your ./local environment or you change
the :origin:`setup.py` file (or the requirements listed in
:origin:`requirements-dev.txt` and :origin:`requirements.txt`), you have to call
:ref:`make clean`.


.. _make run:

``make run``
============

To get up a running a developer instance simply call ``make run``.  This enables
*debug* option in :origin:`searx/settings.yml`, starts a ``./searx/webapp.py``
instance, disables *debug* option again and opens the URL in your favorite WEB
browser (:man:`xdg-open`):

.. code:: sh

  $ make run
  PYENV     usage: source ./local/py3/bin/activate
  PYENV     install .
  ./local/py3/bin/python ./searx/webapp.py
  ...
  INFO:werkzeug: * Running on http://127.0.0.1:8888/ (Press CTRL+C to quit)
  ...

.. _make clean:

``make clean``
==============

Drop all intermediate files, all builds, but keep sources untouched.  Includes
target ``pyclean`` which drops ./local environment.  Before calling ``make
clean`` stop all processes using :ref:`make pyenv`.

.. code:: sh

   $ make clean
   CLEAN     pyclean
   CLEAN     clean

.. _make docs:

``make docs docs-live docs-clean``
==================================

We describe the usage of the ``doc*`` targets in the :ref:`How to contribute /
Documentation <contrib docs>` section.  If you want to edit the documentation
read our :ref:`make docs-live` section.  If you are working in your own brand,
adjust your :ref:`Makefile setup <makefile setup>`.


.. _make gh-pages:

``make gh-pages``
=================

To deploy on github.io first adjust your :ref:`Makefile setup <makefile
setup>`.  For any further read :ref:`deploy on github.io`.

.. _make test:

``make test``
=============

Runs a series of tests: ``test.pep8``, ``test.unit``, ``test.robot`` and does
additional :ref:`pylint checks <make pylint>`.  You can run tests selective,
e.g.:

.. code:: sh

  $ make test.pep8 test.unit test.sh
  . ./local/py3/bin/activate; ./manage.sh pep8_check
  [!] Running pep8 check
  . ./local/py3/bin/activate; ./manage.sh unit_tests
  [!] Running unit tests

.. _make pylint:

``make pylint``
===============

.. _Pylint: https://www.pylint.org/

Before commiting its recommend to do some (more) linting.  Pylint_ is known as
one of the best source-code, bug and quality checker for the Python programming
language.  Pylint_ is not yet a quality gate within our searx project (like
:ref:`test.pep8 <make test>` it is), but Pylint_ can help to improve code
quality anyway.  The pylint profile we use at searx project is found in
project's root folder :origin:`.pylintrc`.

Code quality is a ongoing process.  Don't try to fix all messages from Pylint,
run Pylint and check if your changed lines are bringing up new messages.  If so,
fix it.  By this, code quality gets incremental better and if there comes the
day, the linting is balanced out, we might decide to add Pylint as a quality
gate.


``make pybuild``
================

.. _PyPi: https://pypi.org/
.. _twine: https://twine.readthedocs.io/en/latest/

Build Python packages in ``./dist/py``.

.. code:: sh

  $ make pybuild
  ...
  BUILD     pybuild
  running sdist
  running egg_info
  ...
  $ ls  ./dist/py/
  searx-0.15.0-py3-none-any.whl  searx-0.15.0.tar.gz

To upload packages to PyPi_, there is also a ``upload-pypi`` target.  It needs
twine_ to be installed.  Since you are not the owner of :pypi:`searx` you will
never need the latter.
