===============================
Query more of your NoSQL stores
===============================

From now on, searx lets you to query your NoSQL data stores:

* `Redis`_
* `MongoDB`_

The reference configuration of the engines are included ``settings.yml`` just commented out,
as you have to set various options and install dependencies before using them.

By default, the engines use ``key-value`` template for displaying results.
If you are not satisfied with the original result layout,
you can use your owm template by placing the template under
``searx/templates/{theme_name}/result_templates/{template_name}`` and setting
``result_template`` attribute to ``{template_name}``.

Futhermore, if you do not want to expose these engines on a public instance, you can
still add them and limit the access by setting ``tokens`` as described in the `blog post about
private engines`_.

Configuring searx to use the stores
===================================

NoSQL data stores are used for storing arbitrary data without first defining their
structure.

Redis
-----

Reqired package: ``redis``

Redis is a key value based data store usually stored in memory. 

Select a database to search in and set its index in the option ``db``. You can
either look for exact matches or use partial keywords to find what you are looking for
by configuring ``exact_match_only``.

In this example you can search for exact matches in your first database:

.. code:: yaml

  - name : mystore
    engine : redis_server
    exact_match_only : True
    host : 127.0.0.1
    port : 6379
    password : secret-password
    db : 0
    shortcut : rds
    enable_http : True


MongoDB
-------

Required package: ``pymongo``

MongoDB is a document based database program that handles JSON like data. 

In order to query MongoDB, you have to select a ``database`` and a ``collection``. Furthermore,
you have to select a ``key`` that is going to be searched. MongoDB also supports the option ``exact_match_only``, so configure it
as you wish.

Above is an example configuration for using a MongoDB collection:

.. code:: yaml

  - name : mymongo
    engine : mongodb
    shortcut : md
    host : '127.0.0.1'
    port : 27017
    database : personal
    collection : income
    key : month
    enable_http: True


Acknowledgement
===============

This development was sponsored by `Search and Discovery Fund`_ of `NLnet Foundation`_ .

.. _Redis: https://redis.io/
.. _MongoDB: https://mongodb.com/
.. _blog post about private engines: private-engines.html#private-engines
.. _Search and Discovery Fund: https://nlnet.nl/discovery
.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2021.07.13 23:16

