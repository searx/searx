.. _devquickstart:

======================
Development Quickstart
======================

.. _npm: https://www.npmjs.com/

Searx loves developers, just clone and start hacking.  All the rest is done for
you simply by using :ref:`make <makefile>`.

.. code:: sh

    git clone https://github.com/searx/searx.git

Here is how a minimal workflow looks like:

1. *start* hacking
2. *run* your code: :ref:`make run`
3. *test* your code: :ref:`make test`

If you think at some point something fails, go back to *start*.  Otherwise,
choose a meaningful commit message and we are happy to receive your pull
request. To not end in *wild west* we have some directives, please pay attention
to our ":ref:`how to contribute`" guideline.

If you implement themes, you will need to compile styles and JavaScript before
*run*.

.. code:: sh

   make themes

Don't forget to install npm_ first.

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H apt-get install npm

   .. group-tab:: Arch Linux

      .. code-block:: sh

         sudo -H pacman -S npm

   .. group-tab::  Fedora / RHEL

      .. code-block:: sh

	 sudo -H dnf install npm

