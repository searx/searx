.. _installation docker:

===================
Docker installation
===================

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

Make sure you have installed Docker.  For instance, you can deploy searx like this:

.. code:: sh

    docker pull wonderfall/searx
    docker run -d --name searx -p $PORT:8888 wonderfall/searx

Go to ``http://localhost:$PORT``.

See https://hub.docker.com/r/wonderfall/searx/ for more informations.  It's also
possible to build searx from the embedded Dockerfile.

.. code:: sh

   git clone https://github.com/asciimoo/searx.git
   cd searx
   docker build -t whatever/searx .
