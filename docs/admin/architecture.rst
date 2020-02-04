.. _architecture:

============
Architecture
============

.. sidebar:: Tooling box

   - :ref:`searx & uwsgi <searx.sh>`
   - :ref:`filtron <filtron.sh>`
   - :ref:`reverse proxy`
   - :ref:`morty <morty.sh>`

Herein you will find some hints and suggestions about typical architectures of
searx infrastructures.

We start with a contribution from :pull:`@dalf <1776#issuecomment-567917320>`.
It shows a *reference* setup for public searx instances which can build up and
maintained by the scripts from our :ref:`toolboxing`.

.. _arch public:

.. kernel-figure:: arch_public.dot
   :alt: arch_public.dot

   Reference architecture of a public searx setup.
