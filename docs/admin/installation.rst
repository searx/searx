.. _installation:

============
Installation
============

*You're spoilt for choice*, choose your preferred method of installation.

- :ref:`installation docker`
- `Installation scripts`_
- :ref:`installation basic`

The :ref:`installation basic` is good enough for intranet usage and it is a
excellent illustration of *how a searx instance is build up*.  If you place your
instance public to the internet you should really consider to install a
:ref:`filtron reverse proxy <filtron.sh>` and for privacy a :ref:`result proxy
<morty.sh>` is mandatory.

Therefore, if you do not have any special preferences, its recommend to use the
:ref:`installation docker` or the `Installation scripts`_ from our :ref:`tooling
box <toolboxing>` as described below.


Installation scripts
====================

The following will install a setup as shown in :ref:`architecture`.  First you
need to get a clone.  The clone is only needed for the installation procedure
and some maintenance tasks (alternatively you can create your own fork).

.. code:: bash

   $ cd ~/Download
   $ git clone https://github.com/asciimoo/searx searx
   $ cd searx

.. hint::

   The *tooling box* is not yet merged into `asciimoo/searx master
   <https://github.com/asciimoo/searx>`_.  As long as PR is not merged, you need
   to merge the PR into your local clone (see below).  The discussion takes
   place in :pull:`1803`.  To merge the :pull:`1803` in your local branch use:

   .. code:: bash

      $ git pull origin refs/pull/1803/head

**Install** :ref:`searx service <searx.sh>`

This installs searx as described in :ref:`installation basic`.

.. code:: bash

   $ sudo -H ./utils/searx.sh install all

**Install** :ref:`filtron reverse proxy <filtron.sh>`

.. code:: bash

   $ sudo -H ./utils/filtron.sh install all

**Install** :ref:`result proxy <morty.sh>`

.. code:: bash

   $ sudo -H ./utils/morty.sh install all
