.. _translation:

===========
Translation
===========

.. _searx@transifex: https://www.transifex.com/asciimoo/searx/

Translation currently takes place on `searx@transifex`_

Requirements
============

* Transifex account
* Installed CLI tool of Transifex

Init Transifex project
======================

After installing ``transifex`` using pip, run the following command to
initialize the project.

.. code:: sh

   tx init # Transifex instance: https://www.transifex.com/asciimoo/searx/


After ``$HOME/.transifexrc`` is created, get a Transifex API key and insert it
into the configuration file.

Create a configuration file for ``tx`` named ``$HOME/.tx/config``.

.. code:: ini

    [main]
    host = https://www.transifex.com
    [searx.messagespo]
    file_filter = searx/translations/<lang>/LC_MESSAGES/messages.po
    source_file = messages.pot
    source_lang = en
    type = PO


Then run ``tx set``:

.. code:: shell

    tx set --auto-local -r searx.messagespo 'searx/translations/<lang>/LC_MESSAGES/messages.po' \
    --source-lang en --type PO --source-file messages.pot --execute


Update translations
===================

To retrieve the latest translations, pull it from Transifex.

.. code:: sh

   tx pull -a

Then check the new languages.  If strings translated are not enough, delete those
folders, because those should not be compiled.  Call the command below to compile
the ``.po`` files.

.. code:: shell

   pybabel compile -d searx/translations


After the compilation is finished commit the ``.po`` and ``.mo`` files and
create a PR.
