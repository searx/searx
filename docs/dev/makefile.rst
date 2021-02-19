.. _makefile:

================
Makefile Targets
================

.. _gnu-make: https://www.gnu.org/software/make/manual/make.html#Introduction

.. sidebar:: build environment

   Before looking deeper at the targets, first read about :ref:`make pyenv`.

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

.. _make pyenv:

Python environment
==================

.. sidebar:: activate environment

   ``source ./local/py3/bin/activate``

With Makefile we do no longer need to build up the virtualenv manually. Jump
into your git working tree and release a ``make pyenv``:

.. code:: sh

   $ cd ~/searx-clone
   $ make pyenv
   PYENV     [virtualenv] usage: source ./local/py3/bin/activate
   PYENV     [virtualenv] installing requirements*.txt into ./local/py3
   ...
   Successfully installed ...

With target ``pyenv`` a development environment (aka virtualenv) was build up in
``./local/py3/``.  To make a *developer install* of searx (:origin:`setup.py`)
into this environment, use make target ``install``:

.. code:: text

   $ make install
   PYENV     [virtualenv] usage: source ./local/py3/bin/activate
   PYENV     [virtualenv] using ./local/py3 // glob pattern requirements*.txt --> sha256 OK
   ...
   ModuleNotFoundError: No module named 'searx'
   PYENV     [pyenvinstall]  pip install -e .\[test\]
   ...
     Running setup.py develop for searx
   Successfully installed ... searx ...

You have never to think about intermediate targets like ``pyenv`` or
``install``, the ``Makefile`` chains them as requisites.  Just run your main
target.

.. sidebar:: drop environment

   To get rid of the existing environment before re-build use: :ref:`make clean`

If you think, something goes wrong with your ``./local`` environment or you
change the :origin:`setup.py` file (or the requirements listed in
:origin:`requirements-dev.txt` and :origin:`requirements.txt`), you have to call
:ref:`make clean`.

``PYENV_REQ``: requirement files (glob pattern: ``requirements*.txt``)
  For ever reasons, if you want to install only ``requirements.txt``

  .. code:: text

     $ make PYENV_REQ=requirements.txt clean pyenv
     make PYENV_REQ=requirements.txt clean pyenv
     CLEAN     ...
     ...
     PYENV     [virtualenv] usage: source ./local/py3/bin/activate
     PYENV     [virtualenv] installing requirements.txt into ./local/py3
     ...
     Successfully installed ...


.. _make run:

``make run``
============

To get up a running a developer instance simply call ``make run``.  This enables
*debug* option in :origin:`searx/settings.yml`, starts a ``./searx/webapp.py``
instance, disables *debug* option again and opens the URL in your favorite WEB
browser (:man:`xdg-open`):

.. code:: sh

  $ make run
  PYENV     [virtualenv] usage: source ./local/py3/bin/activate
  PYENV     [virtualenv] installing requirements*.txt into ./local/py3
  ...
  PYENV     [pyenvinstall] pip install -e .\[test\]
  ...
    Running setup.py develop for searx
  Successfully installed searx
  ...
  SEARX_DEBUG=1 ./local/py3/bin/python ./searx/webapp.py
  ...
  INFO:werkzeug: * Running on http://127.0.0.1:8888/ (Press CTRL+C to quit)
  ...

.. _make clean:

``make clean``
==============

Drop all intermediate files, all builds, but keep sources untouched.  Includes
target ``pyclean`` which drops ./local environment.  Before calling ``make
clean`` stop all processes using :ref:`make pyenv`.

.. code:: text

   make clean
   CLEAN     pyclean
   CLEAN     docs-clean
   CLEAN     locally installed npm dependencies
   CLEAN     intermediate test stuff
   CLEAN     clean

.. _make docs:

``make docs docs-live docs-clean``
==================================

We describe the usage of the ``doc*`` targets in the :ref:`How to contribute /
Documentation <contrib docs>` section.  If you want to edit the documentation
read our :ref:`make docs-live` section.  If you are working in your own brand,
adjust your :ref:`settings global`.

.. _make books:

``make books/{name}.html books/{name}.pdf``
===========================================

.. _intersphinx: https://www.sphinx-doc.org/en/stable/ext/intersphinx.html
.. _XeTeX: https://tug.org/xetex/

.. sidebar:: info

   To build PDF a XeTeX_ is needed, see :ref:`buildhosts`.


The ``books/{name}.*`` targets are building *books*.  A *book* is a
sub-directory containing a ``conf.py`` file.  One example is the user handbook
which can deployed separately (:origin:`docs/user/conf.py`).  Such ``conf.py``
do inherit from :origin:`docs/conf.py` and overwrite values to fit *book's*
needs.

With the help of Intersphinx_ (:ref:`reST smart ref`) the links to searx’s
documentation outside of the book will be bound by the object inventory of
``DOCS_URL``.  Take into account that URLs will be picked from the inventary at
documentation's build time.

Use ``make docs-help`` to see which books available:

.. program-output:: bash -c "cd ..; make --no-print-directory docs-help"
   :ellipsis: 0,-6


.. _make gh-pages:

``make gh-pages``
=================

To deploy on github.io first adjust your :ref:`settings global`.  For any
further read :ref:`deploy on github.io`.

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
