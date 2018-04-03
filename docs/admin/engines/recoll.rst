======
Recoll
======

Recoll is a local search engine based on Xapian:
http://www.lesbonscomptes.com/recoll/

By itself recoll does not offer web or API access,
this can be achieved using recoll-webui:
https://github.com/koniu/recoll-webui

As recoll-webui by default does not support paged JSON
results it is advisable to use a patched version which does:
https://github.com/Yetangitu/recoll-webui/tree/jsonpage.

Configuration
-------------

You must configure the following settings:

``base_url``: location where recoll-webui can be reached
``mount_prefix``: location where the file hierarchy is mounted on your _local_ filesystem
``dl_prefix``: location where the file hierarchy as indexed by recoll can be reached
``search_dir``: part of the indexed file hierarchy to be search, if empty the full domain is searched

Example:

Recoll indexes a local filesystem mounted in /export/documents/reference
The Recoll search inteface can be reached at https://recoll.example.org/
The contents of this filesystem can be reached though https://download.example.org/reference


.. code:: yaml
    base_url: https://recoll.example.org/
    mount_prefix: /export/documents
    dl_prefix: https://download.example.org
    search_dir: ''

