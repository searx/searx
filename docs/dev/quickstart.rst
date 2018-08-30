.. _devquickstart:

Development Quickstart
----------------------

This quickstart guide gets your environment set up with searx. Furthermore, it gives a
short introduction to the new manage.sh script.

How to setup your development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, clone the source code of searx to the desired folder. In this case the source
is cloned to ~/myprojects/searx. Then create and activate the searx-ve
virtualenv and install the required packages using manage.sh.

.. code:: sh

    cd ~/myprojects
    git clone https://github.com/asciimoo/searx.git
    cd searx
    virtualenv searx-ve
    . ./searx-ve/bin/activate
    ./manage.sh update_dev_packages


How to run tests
~~~~~~~~~~~~~~~~

Tests can be run using the manage.sh script.

Following tests and checks are available:

- Unit tests

- Selenium tests

- PEP8 validation

- Unit test coverage check

For example unit tests are run with the command below:

.. code:: sh

    ./manage.sh unit_tests

For further test options, please consult the help of the manage.sh script.


How to compile styles and javascript
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How to build styles
^^^^^^^^^^^^^^^^^^^

Less is required to build the styles of searx. Less can be installed using either NodeJS or Apt.

.. code:: sh

    sudo apt-get install nodejs
    sudo npm install -g less


OR

.. code:: sh

    sudo apt-get install node-less

After satisfying the requirements styles can be build using manage.sh

.. code:: sh

    ./manage.sh styles


How to build the source of the oscar theme
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Grunt must be installed in order to build the javascript sources. It depends on NodeJS, so first
Node has to be installed.

.. code:: sh

    sudo apt-get install nodejs
    sudo npm install -g grunt-cli

After installing grunt, the files can be built using the following command: 

.. code:: sh

    ./manage.sh grunt_build



Tips for debugging/development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Turn on debug logging
    Whether you are working on a new engine or trying to eliminate a bug, it is always a good idea
    to turn on debug logging. When debug logging is enabled a stack trace appears,
    instead of the cryptic ``Internal Server Error`` message. It can be turned on by setting
    ``debug: False`` to ``debug: True`` in settings.yml.

2. Run ``./manage.sh tests`` before creating a PR.
    Failing build on Travis is common because of PEP8 checks. So a new commit must be created
    containing these format fixes. This phase can be skipped if ``./manage.sh tests`` is run
    locally before creating a PR.
