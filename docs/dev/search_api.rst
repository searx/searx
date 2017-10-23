Search API
==========

The search supports both ``GET`` and ``POST``.

Furthermore, two enpoints ``/`` and ``/search`` are available for querying.


``GET /``

``GET /search``

Parameters
~~~~~~~~~~

.. code:: sh

    q

The search query. This string is passed to external search services.
Thus, searx supports syntax of each search service. For example, ``site:github.com searx`` is a valid
query for Google. However, if simply the query above is passed to any search engine which does not filter its
results based on this syntax, you might not get the results you wanted.


See more at :doc:`/user/search_syntax`

Required.

.. code:: sh

    categories

Comma separated list, specifies the active search categories

Optional.

.. code:: sh

    engines

Comma separated list, specifies the active search engines.

Optional.

.. code:: sh

    lang

Code of the language.

Optional.

Default: ``all``

.. code:: sh

    pageno

Search page number.

Optional.

Default: ``1``

.. code:: sh

    time_range

Time range of search for engines which support it. See if an engine supports time range search in the preferences page of an instance.

Optional.

Possible: ``day``, ``month``, ``year``

.. code:: sh

    format

Output format of results.

Optional.

Possible: ``json``, ``csv``, ``rss``

.. code:: sh

    results_on_new_tab

Open search results on new tab.

Optional.

Default: ``0``

Possible: ``0``, ``1``

.. code:: sh

    image_proxy

Proxy image results through searx.

Optional.

Default: ``False``

Possible: ``True``, ``False``

.. code:: sh

    autocomplete

Service which completes words as you type.

Optional.

Default: empty

Possible: ``google``, ``dbpedia``, ``duckduckgo``, ``startpage``, ``wikipedia``

.. code:: sh

    safesearch

Filter search results of engines which support safe search. See if an engine supports safe search in the preferences page of an instance.

Optional.

Default: ``None``

Possible: ``0``, ``1``, ``None``

.. code:: sh

    theme

Theme of instance.

Optional.

Default: ``oscar``

Possible: ``oscar``, ``simple``, ``legacy``, ``pix-art``, ``courgette``

Please note, available themes depend on an instance. It is possible that an instance administrator deleted, created or renamed themes on his/her instance. See the available options in the preferences page of the instance.

.. code:: sh

    oscar-style

Style of Oscar theme. It is only parsed if the theme of an instance is ``oscar``.

Optional.

Default: ``logicodev``

Possible: ``pointhi``, ``logicodev``

Please note, available styles depend on an instance. It is possible that an instance administrator deleted, created or renamed styles on his/her instance. See the available options in the preferences page of the instance.

.. code:: sh

    enabled_plugins

List of enabled plugins.

Optional.

Default: ``HTTPS_rewrite``, ``Self_Informations``, ``Search_on_category_select``, ``Tracker_URL_remover``

Possible: ``DOAI_rewrite``, ``HTTPS_rewrite``, ``Infinite_scroll``, ``Vim-like_hotkeys``, ``Self_Informations``, ``Tracker_URL_remover``, ``Search_on_category_select``

.. code:: sh

    disabled_plugins

List of disabled plugins.

Optional.

Default: ``DOAI_rewrite``, ``Infinite_scroll``, ``Vim-like_hotkeys``

Possible: ``DOAI_rewrite``, ``HTTPS_rewrite``, ``Infinite_scroll``, ``Vim-like_hotkeys``, ``Self_Informations``, ``Tracker_URL_remover``, ``Search_on_category_select``

.. code:: sh

    enabled_engines

List of enabled engines.

Optional.

Possible:  all engines

.. code:: sh

    disabled_engines

List of disabled engines.

Optional.

Possible: all engines
