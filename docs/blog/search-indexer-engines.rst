===============================
Query your local search engines
===============================

From now on, searx lets you to query your locally running search engines. The following
ones are supported now:

* `Elasticsearch`_
* `Meilisearch`_
* `Solr`_

All of the engines above are added to ``settings.yml`` just commented out, as you have to
``base_url`` for all them.

Please note that if you are not using HTTPS to access these engines, you have to enable
HTTP requests by setting ``enable_http`` to ``True``.

Futhermore, if you do not want to expose these engines on a public instance, you can
still add them and limit the access by setting ``tokens`` as described in the `blog post about
private engines`_.

Configuring searx for search engines
====================================

Each search engine is powerful, capable of full-text search.

Elasticsearch
-------------

Elasticsearch supports numerous ways to query the data it is storing. At the moment
the engine supports the most popular search methods: ``match``, ``simple_query_string``, ``term`` and ``terms``.

If none of the methods fit your use case, you can select ``custom`` query type and provide the JSON payload
searx has to submit to Elasticsearch in ``custom_query_json``.

The following is an example configuration for an Elasticsearch instance with authentication
configured to read from ``my-index`` index.

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


Meilisearch
-----------

This search engine is aimed at individuals and small companies. It is designed for
small-scale (less than 10 million documents) data collections. E.g. it is great for storing
web pages you have visited and searching in the contents later.

The engine supports faceted search, so you can search in a subset of documents of the collection.
Futhermore, you can search in Meilisearch instances that require authentication by setting ``auth_token``.

Here is a simple example to query a Meilisearch instance:

.. code:: yaml

  - name : meilisearch
    engine : meilisearch
    shortcut: mes
    base_url : http://localhost:7700
    index : my-index
    enable_http: True


Solr
----

Solr is a popular search engine based on Lucene, just like Elasticsearch.
But instead of searching in indices, you can search in collections.

This is an example configuration for searching in the collection ``my-collection`` and get
the results in ascending order.

.. code:: yaml

  - name : solr
    engine : solr
    shortcut : slr
    base_url : http://localhost:8983
    collection : my-collection
    sort : asc
    enable_http : True


Next steps
==========

The next step is to add support for various SQL databases.

Acknowledgement
===============

This development was sponsored by `Search and Discovery Fund`_ of `NLnet Foundation`_ .

.. _blog post about private engines: private-engines.html#private-engines
.. _Elasticsearch: https://www.elastic.co/elasticsearch/
.. _Meilisearch: https://www.meilisearch.com/
.. _Solr: https://solr.apache.org/
.. _Search and Discovery Fund: https://nlnet.nl/discovery
.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2021.04.07 23:16

