.. _installation nginx:

==================
Install with nginx
==================

.. _nginx:
   https://docs.nginx.com/nginx/admin-guide/
.. _nginx server configuration:
   https://docs.nginx.com/nginx/admin-guide/web-server/web-server/#setting-up-virtual-servers
.. _nginx beginners guide:
   http://nginx.org/en/docs/beginners_guide.html
.. _Getting Started wiki:
   https://www.nginx.com/resources/wiki/start/

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry


The nginx HTTP server
=====================

If nginx_ is not installed (uwsgi will not work with the package nginx-light)
install it now.


.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H apt-get install nginx

   .. group-tab:: Arch Linux

      .. code-block:: sh

         sudo -H pacman -S nginx-mainline
         sudo -H systemctl enable nginx
         sudo -H systemctl start nginx

   .. group-tab::  Fedora / RHEL

      .. code-block:: sh

         sudo -H dnf install nginx
         sudo -H systemctl enable nginx
         sudo -H systemctl start nginx

Now at http://localhost you should see a *Welcome to nginx!* page, on Fedora you
see a *Fedora Webserver - Test Page*.  The test page comes from the default
`nginx server configuration`_:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         less /etc/nginx/nginx.conf

      there is a line including site configurations from:

      .. code:: nginx

         include /etc/nginx/sites-enabled/*;

   .. group-tab:: Arch Linux

      .. code-block:: sh

         less /etc/nginx/nginx.conf

      in there is a configuration section named ``server``:

      .. code-block:: nginx

         server {
             listen       80;
             server_name  localhost;
             # ...
         }

   .. group-tab::  Fedora / RHEL

      .. code-block:: sh

         less /etc/nginx/nginx.conf

      there is a line including site configurations from:

      .. code:: nginx

          include /etc/nginx/conf.d/*.conf;

.. _nginx searx site:

A searx site
============

.. sidebar:: public to the internet?

   If your searx instance is public, stop here and first install :ref:`filtron
   reverse proxy <filtron.sh>` and :ref:`result proxy morty <morty.sh>`, see
   :ref:`installation scripts`.

Now you have to create a configuration for the searx site.  If nginx_ is new to
you, the `nginx beginners guide`_ is a good starting point and the `Getting
Started wiki`_ is always a good resource *to keep in the pocket*.

.. tabs::

   .. group-tab:: Ubuntu / debian

      Create configuration at ``/etc/nginx/sites-available/searx`` and place a
      symlink to sites-enabled:

      .. code:: sh

         sudo -H ln -s /etc/nginx/sites-available/searx /etc/nginx/sites-enabled/searx

   .. group-tab:: Arch Linux

      In the ``/etc/nginx/nginx.conf`` file, replace the configuration section
      named ``server``.

   .. group-tab::  Fedora / RHEL

      Create configuration at ``/etc/nginx/conf.d/searx`` and place a
      symlink to sites-enabled:

.. tabs::


   .. group-tab:: filtron at ``/`` & ``/morty``

      Use this setup, if your instance is public to the internet:

      .. code:: nginx

         location / {
             proxy_set_header   Host    $http_host;
             proxy_set_header   X-Real-IP $remote_addr;
             proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header   X-Scheme $scheme;
             proxy_pass         http://127.0.0.1:4004/;
         }

      .. code:: nginx

         location /morty {
             proxy_set_header   Host    $http_host;
             proxy_set_header   X-Real-IP $remote_addr;
             proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header   X-Scheme $scheme;
             proxy_pass         http://127.0.0.1:3000/;
         }

      For a fully result proxification add :ref:`morty's <searx_morty>` public
      URL to your :origin:`searx/settings.yml`:

      .. code:: yaml

         result_proxy:
             # replace searx.example.com with your server's public name
             url : http://searx.example.com/


   .. group-tab:: searx at ``/``

      Use this setup only, if your instance is **NOT** public to the internet:

      .. code:: nginx

         server {
             listen 80;
             listen [::]:80;

             # replace searx.example.com with your server's public name
             server_name searx.example.com;

             root /usr/local/searx/searx;

             location /static {
             }

             location / {
                 include uwsgi_params;
                 uwsgi_pass unix:/run/uwsgi/app/searx/socket;
             }
         }

   .. group-tab:: searx at ``/searx``

      Use this setup only, if your instance is **NOT** public to the internet:

      .. code:: nginx

          location /searx/static {
                  alias /usr/local/searx/searx/static;
          }

          location /searx {
                  uwsgi_param SCRIPT_NAME /searx;
                  include uwsgi_params;
                  uwsgi_pass unix:/run/uwsgi/app/searx/socket;
          }


      **OR** using reverse proxy.  Please, note that reverse proxy advised to be
      used in case of single-user or low-traffic instances.

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

      Enable ``base_url`` in :origin:`searx/settings.yml`

      .. code:: yaml

         server:
             # replace searx.example.com with your server's public name
             base_url : http://searx.example.com/searx/


Restart service:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart nginx
         sudo -H systemctl restart uwsgi

   .. group-tab:: Arch Linux

      .. code:: sh

         sudo -H systemctl restart nginx
         sudo -H systemctl restart uwsgi

   .. group-tab:: Fedora

      .. code:: sh

         sudo -H systemctl restart nginx
         sudo -H systemctl restart uwsgi


Disable logs
============

For better privacy you can disable nginx logs in ``/etc/nginx/nginx.conf``.

.. code:: nginx

    http {
        # ...
        access_log /dev/null;
        error_log  /dev/null;
        # ...
    }
