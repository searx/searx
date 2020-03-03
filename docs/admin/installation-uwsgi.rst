.. _searx uwsgi:

=====
uwsgi
=====

Create the configuration ini-file according to your distribution (see below) and
restart the uwsgi application.

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :start-after: START searx uwsgi-description ubuntu-20.04
         :end-before: END searx uwsgi-description ubuntu-20.04


   .. group-tab:: Arch Linux

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :start-after: START searx uwsgi-description arch
         :end-before: END searx uwsgi-description arch


   .. group-tab::  Fedora / RHEL

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :start-after: START searx uwsgi-description fedora
         :end-before: END searx uwsgi-description fedora


.. tabs::

   .. group-tab:: Ubuntu / debian

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :language: ini
         :start-after: START searx uwsgi-appini ubuntu-20.04
         :end-before: END searx uwsgi-appini ubuntu-20.04

   .. group-tab:: Arch Linux

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :language: ini
         :start-after: START searx uwsgi-appini arch
         :end-before: END searx uwsgi-appini arch

   .. group-tab::  Fedora / RHEL

      .. literalinclude:: ../../build/docs/includes/searx.rst
         :language: ini
         :start-after: START searx uwsgi-appini fedora
         :end-before: END searx uwsgi-appini fedora


