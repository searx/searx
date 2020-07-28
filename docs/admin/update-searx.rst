.. _update searx:

=============
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
