.. _installation docker:

===================
Docker installation
===================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

----

Docker image searx/searx
========================


The docker image is `searx/searx <https://hub.docker.com/r/searx/searx>`_ (based on `github.com/searx/searx <https://github.com/searx/searx>`_).

Make sure you have `installed Docker <https://docs.docker.com/get-docker/>`_.  For instance, you can deploy a local instance:

.. code:: sh

    export PORT=80
    docker pull searx/searx
    docker run --rm -d -v ${PWD}/searx:/etc/searx -p $PORT:8080 -e BASE_URL=http://localhost:$PORT/ searx/searx

Go to ``http://localhost:$PORT``.

Inside ``${PWD}/searx``, you will find ``settings.yml`` and ``uwsgi.ini``.
You can modify these files according to your needs  and restart the Docker image.


Command line
------------


.. code:: sh

    docker run --rm -it searx/searx -h

.. program-output:: ../dockerfiles/docker-entrypoint.sh help


Build the image
---------------

It's also possible to build searx from the embedded Dockerfile.

.. code:: sh

   git clone https://github.com/searx/searx.git
   cd searx
   make docker.build


Public instance
===============

If you intend to create a public instance using Docker, see https://github.com/searx/searx-docker
