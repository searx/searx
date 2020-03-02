.. _searx uwsgi:

=====
uwsgi
=====

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


