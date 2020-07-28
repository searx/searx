
.. _snap: https://snapcraft.io
.. _snapcraft LXD: https://snapcraft.io/lxd
.. _LXC/LXD Image Server: https://uk.images.linuxcontainers.org/
.. _LXC: https://linuxcontainers.org/lxc/introduction/
.. _LXD: https://linuxcontainers.org/lxd/introduction/
.. _`LXD@github`: https://github.com/lxc/lxd

.. _archlinux: https://www.archlinux.org/

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
containers, what we call the: *lxc suite*.  The *searx suite*
(:origin:`lxc-searx.env <utils/lxc-searx.env>`) is loaded by default, every time
you start the ``lxc.sh`` script (*you do not need to care about*).

Before you can start with containers, you need to install and initiate LXD_
once::

  $ snap install lxd
  $ lxd init --auto

To make use of the containers from the *searx suite*, you have to build the
:ref:`LXC suite containers <lxc.sh help>` initial.  But be warned, **this might
take some time**::

  $ sudo -H ./utils/lxc.sh build

A cup of coffee later, your LXC suite is build up and you can run whatever task
you want / in a selected or even in all :ref:`LXC suite containers <lxc.sh
help>`.  If you do not want to build all containers, **you can build just
one**::

  $ sudo -H ./utils/lxc.sh build searx-ubu1804

*Good to know ...*

Each container shares the root folder of the repository and the command
``utils/lxc.sh cmd`` **handles relative path names transparent**, compare output
of::

  $ sudo -H ./utils/lxc.sh cmd -- ls -la Makefile
  ...

In the containers, you can run what ever you want, e.g. to start a bash use::

  $ sudo -H ./utils/lxc.sh cmd searx-ubu1804 bash
  INFO:  [searx-ubu1804] bash
  root@searx-ubu1804:/share/searx#

If there comes the time you want to **get rid off all** the containers and
**clean up local images** just type::

  $ sudo -H ./utils/lxc.sh remove
  $ sudo -H ./utils/lxc.sh remove images

.. _lxc.sh install suite:

Install suite
=============

To install the complete :ref:`searx suite (includes searx, morty & filtron)
<lxc-searx.env>` into all LXC_ use::

  $ sudo -H ./utils/lxc.sh install suite

The command above installs a searx suite (see :ref:`installation scripts`).  To
get the IP (URL) of the filtron service in the containers use ``show suite``
command.  To test instances from containers just open the URLs in your
WEB-Browser::

  $ sudo ./utils/lxc.sh show suite | grep filtron
  [searx-ubu1604]  INFO:  (eth0) filtron:    http://n.n.n.246:4004/ http://n.n.n.246/searx
  [searx-ubu1804]  INFO:  (eth0) filtron:    http://n.n.n.147:4004/ http://n.n.n.147/searx
  [searx-ubu1910]  INFO:  (eth0) filtron:    http://n.n.n.140:4004/ http://n.n.n.140/searx
  [searx-ubu2004]  INFO:  (eth0) filtron:    http://n.n.n.18:4004/ http://n.n.n.18/searx
  [searx-fedora31]  INFO:  (eth0) filtron:    http://n.n.n.46:4004/ http://n.n.n.46/searx
  [searx-archlinux]  INFO:  (eth0) filtron:    http://n.n.n.32:4004/ http://n.n.n.32/searx

To :ref:`install a nginx <installation nginx>` reverse proxy for filtron and
morty use (or alternatively use :ref:`apache <installation apache>`)::

    sudo -H ./utils/lxc.sh cmd -- FORCE_TIMEOUT=0 ./utils/filtron.sh nginx install
    sudo -H ./utils/lxc.sh cmd -- FORCE_TIMEOUT=0 ./utils/morty.sh nginx install


Running commands
================

**Inside containers, you can use make or run scripts** from the
:ref:`toolboxing`.  By example: to setup a :ref:`buildhosts` and run the
Makefile target ``test`` in the archlinux_ container::

  sudo -H ./utils/lxc.sh cmd searx-archlinux ./utils/searx.sh install buildhost
  sudo -H ./utils/lxc.sh cmd searx-archlinux make test


Setup searx buildhost
=====================

You can **install the searx buildhost environment** into one or all containers.
The installation procedure to set up a :ref:`build host<buildhosts>` takes its
time.  Installation in all containers will take more time (time for another cup
of coffee).::

  sudo -H ./utils/lxc.sh cmd -- ./utils/searx.sh install buildhost

To build (live) documentation inside a archlinux_ container::

  sudo -H ./utils/lxc.sh cmd searx-archlinux make docs-clean docs-live
  ...
  [I 200331 15:00:42 server:296] Serving on http://0.0.0.0:8080

To get IP of the container and the port number *live docs* is listening::

  $ sudo ./utils/lxc.sh show suite | grep docs-live
  ...
  [searx-archlinux]  INFO:  (eth0) docs-live:  http://n.n.n.12:8080/


.. _lxc.sh help:

Overview
========

The ``--help`` output of the script is largely self-explanatory:

.. program-output:: ../utils/lxc.sh --help


.. _lxc-searx.env:

searx suite
===========

.. literalinclude:: ../../utils/lxc-searx.env
   :language: bash
