.. _installation:

Installation
============

.. contents::
   :depth: 3

Basic installation
------------------

Step by step installation for Debian/Ubuntu with virtualenv. For Ubuntu, be sure to have enable universe repository.

Install packages:

.. code:: sh

    sudo apt-get install git build-essential libxslt-dev python-dev python-virtualenv python-babel zlib1g-dev libffi-dev libssl-dev

Install searx:

.. code:: sh

    cd /usr/local
    sudo git clone https://github.com/asciimoo/searx.git
    sudo useradd searx -d /usr/local/searx
    sudo chown searx:searx -R /usr/local/searx

Install dependencies in a virtualenv:

.. code:: sh

    sudo -u searx -i
    cd /usr/local/searx
    virtualenv searx-ve
    . ./searx-ve/bin/activate
    ./manage.sh update_packages

Configuration
-------------

.. code:: sh

    sed -i -e "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml

Edit searx/settings.yml if necessary.

Check
-----

Start searx:

.. code:: sh

    python searx/webapp.py

Go to http://localhost:8888

If everything works fine, disable the debug option in settings.yml:

.. code:: sh

    sed -i -e "s/debug : True/debug : False/g" searx/settings.yml

At this point searx is not demonized ; uwsgi allows this.

You can exit the virtualenv and the searx user bash (enter exit command
twice).

uwsgi
-----

Install packages:

.. code:: sh

    sudo apt-get install uwsgi uwsgi-plugin-python

Create the configuration file /etc/uwsgi/apps-available/searx.ini with
this content:

::

    [uwsgi]
    # Who will run the code
    uid = searx
    gid = searx

    # disable logging for privacy
    disable-logging = true

    # Number of workers (usually CPU count)
    workers = 4

    # The right granted on the created socket
    chmod-socket = 666

    # Plugin to use and interpretor config
    single-interpreter = true
    master = true
    plugin = python
    lazy-apps = true
    enable-threads = true

    # Module to import
    module = searx.webapp

    # Virtualenv and python path
    virtualenv = /usr/local/searx/searx-ve/
    pythonpath = /usr/local/searx/
    chdir = /usr/local/searx/searx/

Activate the uwsgi application and restart:

.. code:: sh

    cd /etc/uwsgi/apps-enabled
    ln -s ../apps-available/searx.ini
    /etc/init.d/uwsgi restart

Web server
----------

with nginx
^^^^^^^^^^

If nginx is not installed (uwsgi will not work with the package
nginx-light):

.. code:: sh

    sudo apt-get install nginx

Hosted at /
"""""""""""

Create the configuration file /etc/nginx/sites-available/searx with this
content:

.. code:: nginx

    server {
        listen 80;
        server_name searx.example.com;
        root /usr/local/searx;

        location / {
                include uwsgi_params;
                uwsgi_pass unix:/run/uwsgi/app/searx/socket;
        }
    }

Create a symlink to sites-enabled:

.. code:: sh

   sudo ln -s /etc/nginx/sites-available/searx /etc/nginx/sites-enabled/searx

Restart service:

.. code:: sh

    sudo service nginx restart
    sudo service uwsgi restart

from subdirectory URL (/searx)
""""""""""""""""""""""""""""""

Add this configuration in the server config file
/etc/nginx/sites-enabled/default:

.. code:: nginx

    location = /searx { rewrite ^ /searx/; }
    location /searx {
            try_files $uri @searx;
    }
    location @searx {
            uwsgi_param SCRIPT_NAME /searx;
            include uwsgi_params;
            uwsgi_modifier1 30;
            uwsgi_pass unix:/run/uwsgi/app/searx/socket;
    }


OR

using reverse proxy
(Please, note that reverse proxy advised to be used in case of single-user or low-traffic instances.)

.. code:: nginx

    location /searx {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /searx;
        proxy_buffering off;
    }


Enable base\_url in searx/settings.yml

::

    base_url : http://your.domain.tld/searx/

Restart service:

.. code:: sh

    sudo service nginx restart
    sudo service uwsgi restart

disable logs
~~~~~~~~~~~~

for better privacy you can disable nginx logs about searx.

how to proceed: below ``uwsgi_pass`` in
/etc/nginx/sites-available/default add

::

    access_log /dev/null;
    error_log /dev/null;

Restart service:

.. code:: sh

    sudo service nginx restart

with apache
^^^^^^^^^^^

Add wsgi mod:

.. code:: sh

    sudo apt-get install libapache2-mod-uwsgi
    sudo a2enmod uwsgi

Add this configuration in the file /etc/apache2/apache2.conf:

.. code:: apache

    <Location />
        Options FollowSymLinks Indexes
        SetHandler uwsgi-handler
        uWSGISocket /run/uwsgi/app/searx/socket
    </Location>

Note that if your instance of searx is not at the root, you should
change ``<Location />`` by the location of your instance, like
``<Location /searx>``.

Restart Apache:

.. code:: sh

    sudo /etc/init.d/apache2 restart

disable logs
""""""""""""

For better privacy you can disable Apache logs.

WARNING: not tested

WARNING: you can only disable logs for the whole (virtual) server not
for a specific path.

Go back to /etc/apache2/apache2.conf and above ``<Location />`` add:

.. code:: apache

    CustomLog /dev/null combined

Restart Apache:

.. code:: sh

    sudo /etc/init.d/apache2 restart

How to update
-------------

.. code:: sh

    cd /usr/local/searx
    sudo -u searx -i
    . ./searx-ve/bin/activate
    git stash
    git pull origin master
    git stash apply
    ./manage.sh update_packages
    sudo service uwsgi restart

Docker
------

Make sure you have installed Docker. For instance, you can deploy searx like this:

.. code:: sh

    docker pull wonderfall/searx
    docker run -d --name searx -p $PORT:8888 wonderfall/searx

Go to http://localhost:$PORT.

See https://hub.docker.com/r/wonderfall/searx/ for more informations.

It's also possible to build searx from the embedded Dockerfile.

.. code:: sh

    git clone https://github.com/asciimoo/searx.git
    cd searx
    docker build -t whatever/searx .

References
==========

    * https://about.okhin.fr/posts/Searx/ with some additions

    * How to: `Setup searx in a couple of hours with a free SSL certificate <https://www.reddit.com/r/privacytoolsIO/comments/366kvn/how_to_setup_your_own_privacy_respecting_search/>`__

