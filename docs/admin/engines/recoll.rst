.. _engine recoll:

======
Recoll
======

.. sidebar:: info

   - `Recoll <https://www.lesbonscomptes.com/recoll/>`_
   - `recoll-webui <https://github.com/koniu/recoll-webui>`_
   - branch `jsonpage@Yetangitu
     <https://github.com/Yetangitu/recoll-webui/tree/jsonpage.>`_

Recoll_ is a desktop full-text search tool based on Xapian. By itself Recoll_
does not offer web or API access, this can be achieved using recoll-webui_

.. _patched: https://github.com/koniu/recoll-webui/compare/master...Yetangitu:jsonpage

As recoll-webui_ by default does not support paged JSON results it is advisable
to use a patched_ version which does: branch `jsonpage@Yetangitu`_


Configuration
=============

You must configure the following settings:

``base_url``:
  Location where recoll-webui can be reached.

``mount_prefix``:
  Location where the file hierarchy is mounted on your *local* filesystem.

``dl_prefix``:
  Location where the file hierarchy as indexed by recoll can be reached.

``search_dir``:
  Part of the indexed file hierarchy to be search, if empty the full domain is
  searched.


Example
=======

Scenario:

#. Recoll indexes a local filesystem mounted in ``/export/documents/reference``,
#. the Recoll search inteface can be reached at https://recoll.example.org/ and
#. the contents of this filesystem can be reached though https://download.example.org/reference

.. code:: yaml

   base_url: https://recoll.example.org/
   mount_prefix: /export/documents
   dl_prefix: https://download.example.org
   search_dir: ''
