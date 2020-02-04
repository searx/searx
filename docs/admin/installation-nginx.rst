.. _installation nginx:

==================
Install with nginx
==================

.. sidebar:: public HTTP servers

   On public searx instances use an application firewall (:ref:`filtron
   <filtron.sh>`).

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

If nginx is not installed (uwsgi will not work with the package
nginx-light):

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H apt-get install nginx

Hosted at ``/``
===============

Create the configuration file ``/etc/nginx/sites-available/searx`` with this
content:

.. code:: nginx

    server {
        listen 80;
        server_name searx.example.com;
        root /usr/local/searx/searx;

        location /static {
        }

        location / {
                include uwsgi_params;
                uwsgi_pass unix:/run/uwsgi/app/searx/socket;
        }
    }

Create a symlink to sites-enabled:

.. code:: sh

   sudo -H ln -s /etc/nginx/sites-available/searx /etc/nginx/sites-enabled/searx

Restart service:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart nginx
         sudo -H systemctl restart uwsgi

from subdirectory URL (``/searx``)
==================================

Add this configuration in the server config file
``/etc/nginx/sites-enabled/default``:

.. code:: nginx

    location /searx/static {
            alias /usr/local/searx/searx/static;
    }

    location /searx {
            uwsgi_param SCRIPT_NAME /searx;
            include uwsgi_params;
            uwsgi_pass unix:/run/uwsgi/app/searx/socket;
    }


**OR** using reverse proxy (Please, note that reverse proxy advised to be used
in case of single-user or low-traffic instances.)

.. code:: nginx

    location /searx/static {
            alias /usr/local/searx/searx/static;
    }

    location /searx {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /searx;
        proxy_buffering off;
    }

Enable ``base_url`` in ``searx/settings.yml``

.. code:: yaml

    base_url : http://your.domain.tld/searx/

Restart service:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart nginx
         sudo -H systemctl restart uwsgi


disable logs
============

For better privacy you can disable nginx logs about searx.  How to proceed:
below ``uwsgi_pass`` in ``/etc/nginx/sites-available/default`` add:

.. code:: nginx

    access_log /dev/null;
    error_log /dev/null;

Restart service:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart nginx
