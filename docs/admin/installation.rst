.. _installation:

============
Installation
============

.. sidebar:: Searx server setup

   - :ref:`installation nginx`
   - :ref:`installation apache`

   If you do not have any special preferences, it is recommend to use
   :ref:`searx.sh`.

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. _installation basic:

Basic installation
==================

Step by step installation with virtualenv.  For Ubuntu, be sure to have enable
universe repository.

Install packages:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code-block:: sh

         $ sudo -H apt-get install \
                   git build-essential
                   libxslt-dev python3-dev python3-babel \
                   zlib1g-dev libffi-dev libssl-dev

Install searx:

.. code:: sh

    sudo -H useradd searx --system --disabled-password -d /usr/local/searx
    sudo -H usermod -a -G shadow $SERVICE_USER
    cd /usr/local/searx
    sudo -H git clone https://github.com/asciimoo/searx.git searx-src
    sudo -H chown searx:searx -R /usr/local/searx

Install virtualenv:

.. code:: sh

    sudo -H -u searx -i
    (searx)$ python3 -m venv searx-pyenv
    (searx)$ echo 'source ~/searx-pyenv/bin/activate' > ~/.profile

Exit the searx bash and restart a new to install the searx dependencies:

.. code:: sh

    sudo -H -u searx -i
    (searx)$ cd searx-src
    (searx)$ ./manage.sh update_packages

Configuration
==============

.. code:: sh

    sudo -H -u searx -i
    (searx)$ cd searx-src
    (searx)$ sed -i -e "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml

Edit searx/settings.yml if necessary.

Check
=====

Start searx:

.. code:: sh

    sudo -H -u searx -i
    (searx)$ cd searx-src
    (searx)$ python3 searx/webapp.py

Go to http://localhost:8888

If everything works fine, disable the debug option in settings.yml:

.. code:: sh

    sed -i -e "s/debug : True/debug : False/g" searx/settings.yml

At this point searx is not demonized ; uwsgi allows this.  You can exit the
virtualenv and the searx user bash (enter exit command twice).

uwsgi
=====

Install packages:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code-block:: bash

         sudo -H apt-get install uwsgi uwsgi-plugin-python3

Create the configuration file ``/etc/uwsgi/apps-available/searx.ini`` with this
content:

.. code:: ini

   [uwsgi]

   # uWSGI core
   # ----------
   #
   # https://uwsgi-docs.readthedocs.io/en/latest/Options.html#uwsgi-core

   # Who will run the code
   uid = searx
   gid = searx

   # chdir to specified directory before apps loading
   chdir = /usr/local/searx/searx-src/searx

   # disable logging for privacy
   disable-logging = true

   # The right granted on the created socket
   chmod-socket = 666

   # Plugin to use and interpretor config
   single-interpreter = true

   # enable master process
   master = true

   # load apps in each worker instead of the master
   lazy-apps = true

   # load uWSGI plugins
   plugin = python3,http

   # By default the Python plugin does not initialize the GIL.  This means your
   # app-generated threads will not run.  If you need threads, remember to enable
   # them with enable-threads.  Running uWSGI in multithreading mode (with the
   # threads options) will automatically enable threading support. This *strange*
   # default behaviour is for performance reasons.
   enable-threads = true

   # plugin: python
   # --------------
   #
   # https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugin-python

   # load a WSGI module
   module = searx.webapp

   # set PYTHONHOME/virtualenv
   virtualenv = /usr/local/searx/searx-pyenv

   # add directory (or glob) to pythonpath
   pythonpath = /usr/local/searx/searx-src


   # plugin http
   # -----------
   #
   # https://uwsgi-docs.readthedocs.io/en/latest/Options.html#plugin-http

   # Native HTTP support: https://uwsgi-docs.readthedocs.io/en/latest/HTTP.html
   http = 127.0.0.1:8888

Activate the uwsgi application and restart:

.. code:: sh

    cd /etc/uwsgi/apps-enabled
    ln -s ../apps-available/searx.ini
    /etc/init.d/uwsgi restart


How to update
=============

.. code:: sh

    sudo -H -u searx -i
    (searx)$ git stash
    (searx)$ git pull origin master
    (searx)$ git stash apply
    (searx)$ ./manage.sh update_packages

Restart uwsgi:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart uwsgi

Docker
======

Make sure you have installed Docker. For instance, you can deploy searx like this:

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

References
==========

* https://about.okhin.fr/posts/Searx/ with some additions

* How to: `Setup searx in a couple of hours with a free SSL certificate
  <https://www.reddit.com/r/privacytoolsIO/comments/366kvn/how_to_setup_your_own_privacy_respecting_search/>`__
