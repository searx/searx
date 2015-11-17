Translation
===========

run these commands in the root directory of searx

Add new language
~~~~~~~~~~~~~~~~

``pybabel init -i messages.pot -d searx/translations -l it``

Update .po files
~~~~~~~~~~~~~~~~

``./utils/update-translations.sh``

You may have errors here. In that case, edit the
``update-translations.sh`` script to change ``pybabel`` to
``pybabel-python2``

After this step, you can modify the .po files.

Compile translations
~~~~~~~~~~~~~~~~~~~~

``pybabel compile -d searx/translations``

Transifex stuff
~~~~~~~~~~~~~~~

Init Project
^^^^^^^^^^^^

.. code:: shell

    tx set --auto-local -r searx.messagespo 'searx/translations/<lang>/LC_MESSAGES/messages.po' \
    --source-lang en --type PO --source-file messages.pot --execute

http://docs.transifex.com/developer/client/set

*TODO: mapping between transifex and searx*

Get translations
^^^^^^^^^^^^^^^^

.. code:: shell

    tx pull -a

http://docs.transifex.com/developer/client/pull

Upload source File
^^^^^^^^^^^^^^^^^^

::

    tx push -s

Upload all Translation
^^^^^^^^^^^^^^^^^^^^^^

::

    tx push -s -t

upload specifc Translation (only for admins)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    tx push -t -l tr

http://docs.transifex.com/developer/client/push

*TODO: upload empty files? (new translations)*
