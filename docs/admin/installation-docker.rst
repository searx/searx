.. _installation docker:

===================
Docker installation
===================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

----

Docker image searxng/searxng
============================


The docker image is `searxng/searxng <https://hub.docker.com/r/searxng/searxng>`_ (based on `github.com/searxng/searxng <https://github.com/searxng/searxng>`_).

Make sure you have `installed Docker <https://docs.docker.com/get-docker/>`_.  For instance, you can deploy a local instance:

.. code:: sh

    export PORT=80
    docker pull searxng/searxng
    docker run --rm -d -v ${PWD}/searx:/etc/searx -p $PORT:8080 -e BASE_URL=http://localhost:$PORT/ searxng/searxng

Go to ``http://localhost:$PORT``.

Inside ``${PWD}/searx``, you will find ``settings.yml`` and ``uwsgi.ini``.
You can modify these files according to your needs  and restart the Docker image.


Command line
------------


.. code:: sh

    docker run --rm -it searxng/searxng -h

.. program-output:: ../dockerfiles/docker-entrypoint.sh -h


Build the image
---------------

It's also possible to build SearXNG from the embedded Dockerfile.

.. code:: sh

   git clone https://github.com/searxng/searxng.git
   cd searx
   make docker.build


Public instance
===============

If you intend to create a public instance using Docker, see https://github.com/searx/searx-docker
