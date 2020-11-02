.. template evaluated by: ./utils/searx.sh docs
.. hint: all dollar-names are variables, dollar sign itself is quoted by: \\$

.. START distro-packages

.. tabs::

  .. group-tab:: Ubuntu / debian

    .. code-block:: sh

      $ sudo -H apt-get install -y \\
${debian}

  .. group-tab:: Arch Linux

    .. code-block:: sh

      $ sudo -H pacman -S --noconfirm \\
${arch}

  .. group-tab::  Fedora / RHEL

    .. code-block:: sh

      $ sudo -H dnf install -y \\
${fedora}

.. END distro-packages

.. START build-packages

.. tabs::

  .. group-tab:: Ubuntu / debian

    .. code-block:: sh

      $ sudo -H apt-get install -y \\
${debian_build}

  .. group-tab:: Arch Linux

    .. code-block:: sh

      $ sudo -H pacman -S --noconfirm \\
${arch_build}

  .. group-tab::  Fedora / RHEL

    .. code-block:: sh

      $ sudo -H dnf install -y \\
${fedora_build}

.. END build-packages

.. START create user

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

      $ sudo -H useradd --shell /bin/bash --system \\
          --home-dir \"$SERVICE_HOME\" \\
          --comment 'Privacy-respecting metasearch engine' $SERVICE_USER

      $ sudo -H mkdir \"$SERVICE_HOME\"
      $ sudo -H chown -R \"$SERVICE_GROUP:$SERVICE_GROUP\" \"$SERVICE_HOME\"

.. END create user

.. START clone searx

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

       $ sudo -H -u ${SERVICE_USER} -i
       (${SERVICE_USER})$ git clone \"https://github.com/searx/searx.git\" \"$SEARX_SRC\"

.. END clone searx

.. START create virtualenv

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

       (${SERVICE_USER})$ python3 -m venv \"${SEARX_PYENV}\"
       (${SERVICE_USER})$ echo \". ${SEARX_PYENV}/bin/activate\" >>  \"$SERVICE_HOME/.profile\"

.. END create virtualenv

.. START manage.sh update_packages

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

       $ sudo -H -u ${SERVICE_USER} -i

       (${SERVICE_USER})$ command -v python && python --version
       $SEARX_PYENV/bin/python
       Python 3.8.1

       # update pip's boilerplate ..
       pip install -U pip
       pip install -U setuptools
       pip install -U wheel

       # jump to searx's working tree and install searx into virtualenv
       (${SERVICE_USER})$ cd \"$SEARX_SRC\"
       (${SERVICE_USER})$ pip install -e .


.. END manage.sh update_packages

.. START searx config

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

       $ sudo -H mkdir -p \"$(dirname ${SEARX_SETTINGS_PATH})\"
       $ sudo -H cp \"$SEARX_SRC/searx/settings.yml\" \"${SEARX_SETTINGS_PATH}\"
       $ sudo -H sed -i -e \"s/ultrasecretkey/\$(openssl rand -hex 16)/g\" \"$SEARX_SETTINGS_PATH\"
       $ sudo -H sed -i -e \"s/{instance_name}/searx@\$(uname -n)/g\" \"$SEARX_SETTINGS_PATH\"

.. END searx config

.. START check searx installation

.. tabs::

  .. group-tab:: bash

    .. code-block:: sh

       # enable debug ..
       $ sudo -H sed -i -e \"s/debug : False/debug : True/g\" \"$SEARX_SETTINGS_PATH\"

       # start webapp
       $ sudo -H -u ${SERVICE_USER} -i
       (${SERVICE_USER})$ cd ${SEARX_SRC}
       (${SERVICE_USER})$ export SEARX_SETTINGS_PATH=\"${SEARX_SETTINGS_PATH}\"
       (${SERVICE_USER})$ python searx/webapp.py

       # disable debug
       $ sudo -H sed -i -e \"s/debug : True/debug : False/g\" \"$SEARX_SETTINGS_PATH\"

Open WEB browser and visit http://$SEARX_INTERNAL_URL .  If you are inside a
container or in a script, test with curl:

.. tabs::

  .. group-tab:: WEB browser

    .. code-block:: sh

       $ xdg-open http://$SEARX_INTERNAL_URL

  .. group-tab:: curl

    .. code-block:: none

       $ curl --location --verbose --head --insecure $SEARX_INTERNAL_URL

       *   Trying 127.0.0.1:8888...
       * TCP_NODELAY set
       * Connected to 127.0.0.1 (127.0.0.1) port 8888 (#0)
       > HEAD / HTTP/1.1
       > Host: 127.0.0.1:8888
       > User-Agent: curl/7.68.0
       > Accept: */*
       >
       * Mark bundle as not supporting multiuse
       * HTTP 1.0, assume close after body
       < HTTP/1.0 200 OK
       HTTP/1.0 200 OK
       ...

.. END check searx installation
