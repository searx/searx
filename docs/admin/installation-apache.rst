.. _installation apache:

===================
Install with apache
===================

.. sidebar:: public to the internet?

   If your searx instance is public, stop here and first install :ref:`filtron
   reverse proxy <filtron.sh>` and :ref:`result proxy morty <morty.sh>`, see
   :ref:`installation scripts`.

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

Add wsgi mod
============

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H apt-get install libapache2-mod-uwsgi
         sudo -H a2enmod uwsgi

Add this configuration in the file ``/etc/apache2/apache2.conf``.  To limit
acces to your intranet replace ``Allow from all`` directive and replace
``192.168.0.0/16`` with your subnet IP/class.

.. _inranet apache site:

Note that if your instance of searx is not at the root, you should change
``<Location />`` by the location of your instance, like ``<Location /searx>``:

.. code:: apache

   # CustomLog /dev/null combined

   <IfModule mod_uwsgi.c>

     <Location />

          Options FollowSymLinks Indexes
          SetHandler uwsgi-handler
          uWSGISocket /run/uwsgi/app/searx/socket

          Order deny,allow
          Deny from all
          # Allow from fd00::/8 192.168.0.0/16 fe80::/10 127.0.0.0/8 ::1
          Allow from all

     </Location>

   </IfModule>

Enable apache mod_uwsgi and restart apache:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         a2enmod uwsgi
         sudo -H systemctl restart apache2

disable logs
============

For better privacy you can disable Apache logs.  Go back to
``/etc/apache2/apache2.conf`` :ref:`[example] <inranet apache site>` and above
``<Location />`` activate directive:

.. code:: apache

    CustomLog /dev/null combined

Restart apache:

.. tabs::

   .. group-tab:: Ubuntu / debian

      .. code:: sh

         sudo -H systemctl restart apache2

.. warning::

   You can only disable logs for the whole (virtual) server not for a specific
   path.
