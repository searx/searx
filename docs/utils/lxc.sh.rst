

.. _snap: https://snapcraft.io
.. _snapcraft LXD: https://snapcraft.io/lxd
.. _LXC/LXD Image Server: https://uk.images.linuxcontainers.org/
.. _LXC: https://linuxcontainers.org/lxc/introduction/
.. _LXD: https://linuxcontainers.org/lxd/introduction/
.. _`LXD@github`: https://github.com/lxc/lxd

.. _lxc.sh:

================
``utils/lxc.sh``
================

.. sidebar:: further reading

   - snap_, `snapcraft LXD`_
   - LXC_,  LXD_
   - `LXC/LXD Image Server`_
   - `LXD@github`_

With the use of *Linux Containers* (LXC_) we can scale our tasks over a stack of
containers, what we call the: *lxc suite*.  Before you can start with
containers, you need to install and initiate LXD_ once::

  $ snap install lxd
  $ lxd init --auto

The *searx suite* (:origin:`lxc-searx.env <utils/lxc-searx.env>`) is loaded by
default, every time you start the ``lxc.sh`` script (you do not need to care
about).  To make use of the containers from the *searx suite*, you have to build
the :ref:`LXC suite containers <lxc.sh --help>` first.  But be warned, this
might take some time::

  $ sudo -H ./utils/lxc.sh build

A cup of coffee later, your LXC suite is build up and you can run whatever task
you want / in a selected or even in all :ref:`LXC suite containers <lxc.sh
--help>`.  Each container shares the root folder of the repository and the
command ``utils/lxc.sh cmd`` handles relative path names *transparent*::

  $ sudo -H ./utils/lxc.sh cmd -- ls -la Makefile
  ...
  [searx-ubu2004]   -rw-r--r-- 1 root root 7603 Mar 30 11:54 Makefile
  [searx-fedora31]  -rw-r--r-- 1 root root 7603 Mar 30 11:54 Makefile
  [searx-archlinux] -rw-r--r-- 1 root root 7603 Mar 30 11:54 Makefile

With this in mind, you can run :ref:`searx.sh` and install packages, needed by
searx::

  $ sudo -H ./utils/lxc.sh cmd -- ./utils/searx.sh install packages

And run one of the :origin:`Makefile` targets::

  $ sudo -H ./utils/lxc.sh cmd -- make test.sh

You can install a *buildhost environment* into the containers (time for another
cup of coffee)::

  $ sudo -H ./utils/lxc.sh install buildhost

If you want to get rid off all the containers, just type::

  $ sudo -H ./utils/lxc.sh remove

To clean up your local images use::

  $ sudo -H ./utils/lxc.sh remove images

.. _lxc.sh --help:

Overview
========

The ``--help`` output of the script is largely self-explanatory:

.. program-output:: ../utils/lxc.sh --help

