Translation
===========

run these commands in the root directory of searx

Add new language
~~~~~~~~~~~~~~~~

.. code:: shell

    pybabel init -i messages.pot -d searx/translations -l it

Update .po files
~~~~~~~~~~~~~~~~

.. code:: shell

    ./utils/update-translations.sh

You may have errors here. In that case, edit the
``update-translations.sh`` script to change ``pybabel`` to
``pybabel-python2`` or ``pybabel2``

After this step, you can modify the .po files.

Compile translations
~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    pybabel compile -d searx/translations

Transifex stuff
~~~~~~~~~~~~~~~

Init Project
^^^^^^^^^^^^

.. code:: shell

    tx init # Transifex instance: https://www.transifex.com/asciimoo/searx/

    tx set --auto-local -r searx.messagespo 'searx/translations/<lang>/LC_MESSAGES/messages.po' \
    --source-lang en --type PO --source-file messages.pot --execute

http://docs.transifex.com/client/init/

http://docs.transifex.com/client/set/

Get translations
^^^^^^^^^^^^^^^^

.. code:: shell

    tx pull -a

http://docs.transifex.com/client/pull

Upload source File
^^^^^^^^^^^^^^^^^^

.. code:: shell

    tx push -s

Upload all Translation
^^^^^^^^^^^^^^^^^^^^^^

.. code:: shell

    tx push -s -t

upload specifc Translation
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell

    tx push -t -l tr

http://docs.transifex.com/client/push
