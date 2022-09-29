==================
Search in indexers
==================

Searx supports three popular indexer search engines:

* Elasticsearch
* Meilisearch
* Solr

Elasticsearch
=============

Make sure that the Elasticsearch user has access to the index you are querying.
If you are not using TLS during your connection, set ``enable_http`` to ``True``.

.. code:: yaml

  - name : elasticsearch
    shortcut : es
    engine : elasticsearch
    base_url : http://localhost:9200
    username : elastic
    password : changeme
    index : my-index
    query_type : match
    enable_http : True

Available settings
------------------

* ``base_url``: URL of Elasticsearch instance. By default it is set to ``http://localhost:9200``.
* ``index``: Name of the index to query. Required.
* ``query_type``: Elasticsearch query method to use. Available: ``match``,
  ``simple_query_string``, ``term``, ``terms``, ``custom``.
* ``custom_query_json``: If you selected ``custom`` for ``query_type``, you must
  provide the JSON payload in this option.
* ``username``: Username in Elasticsearch
* ``password``: Password for the Elasticsearch user

Meilisearch
===========

If you are not using TLS during connection, set ``enable_http`` to ``True``.

.. code:: yaml

  - name : meilisearch
    engine : meilisearch
    shortcut: mes
    base_url : http://localhost:7700
    index : my-index
    enable_http: True

Available settings
------------------

* ``base_url``: URL of the Meilisearch instance. By default it is set to http://localhost:7700
* ``index``: Name of the index to query. Required.
* ``auth_key``: Key required for authentication.
* ``facet_filters``: List of facets to search in.

Solr
====

If you are not using TLS during connection, set ``enable_http`` to ``True``.

.. code:: yaml

  - name : solr
    engine : solr
    shortcut : slr
    base_url : http://localhost:8983
    collection : my-collection
    sort : asc
    enable_http : True

Available settings
------------------

* ``base_url``: URL of the Meilisearch instance. By default it is set to http://localhost:8983
* ``collection``: Name of the collection to query. Required.
* ``sort``: Sorting of the results. Available: ``asc``, ``desc``.
* ``rows``: Maximum number of results from a query. Default value: 10.
* ``field_list``: List of fields returned from the query.
* ``default_fields``: Default fields to query.
* ``query_fields``: List of fields with a boost factor. The bigger the boost
  factor of a field, the more important the field is in the query. Example:
  ``qf="field1^2.3 field2"``
