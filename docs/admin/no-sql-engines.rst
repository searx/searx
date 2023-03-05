===========================
Query SQL and NoSQL servers
===========================

SQL
===

SQL servers are traditional databases with predefined data schema. Furthermore,
modern versions also support BLOB data.

You can search in the following servers:

* `PostgreSQL`_
* `MySQL`_
* `SQLite`_

The configuration of the new database engines are similar. You must put a valid
SELECT SQL query in ``query_str``. At the moment you can only bind at most
one parameter in your query.

Do not include LIMIT or OFFSET in your SQL query as the engines
rely on these keywords during paging.

PostgreSQL
----------

Required PyPi package: ``psychopg2``

You can find an example configuration below:

.. code:: yaml

  - name : postgresql
    engine : postgresql
    database : my_database
    username : searx
    password : password
    query_str : 'SELECT * from my_table WHERE my_column = %(query)s'
    shortcut : psql


Available options
~~~~~~~~~~~~~~~~~
* ``host``: IP address of the host running PostgreSQL. By default it is ``127.0.0.1``.
* ``port``: Port number PostgreSQL is listening on. By default it is ``5432``.
* ``database``: Name of the database you are connecting to.
* ``username``: Name of the user connecting to the database.
* ``password``: Password of the database user.
* ``query_str``: Query string to run. Keywords like ``LIMIT`` and ``OFFSET`` are not allowed. Required.
* ``limit``: Number of returned results per page. By default it is 10.

MySQL
-----

Required PyPi package: ``mysql-connector-python``

This is an example configuration for quering a MySQL server:

.. code:: yaml

  - name : mysql
    engine : mysql_server
    database : my_database
    username : searx
    password : password
    limit : 5
    query_str : 'SELECT * from my_table WHERE my_column=%(query)s'
    shortcut : mysql


Available options
~~~~~~~~~~~~~~~~~
* ``host``: IP address of the host running MySQL. By default it is ``127.0.0.1``.
* ``port``: Port number MySQL is listening on. By default it is ``3306``.
* ``database``: Name of the database you are connecting to.
* ``auth_plugin``: Authentication plugin to use. By default it is ``caching_sha2_password``.
* ``username``: Name of the user connecting to the database.
* ``password``: Password of the database user.
* ``query_str``: Query string to run. Keywords like ``LIMIT`` and ``OFFSET`` are not allowed. Required.
* ``limit``: Number of returned results per page. By default it is 10.

SQLite
------

You can read from your database ``my_database`` using this example configuration:

.. code:: yaml

  - name : sqlite
    engine : sqlite
    shortcut: sq
    database : my_database
    query_str : 'SELECT * FROM my_table WHERE my_column=:query'


Available options
~~~~~~~~~~~~~~~~~
* ``database``: Name of the database you are connecting to.
* ``query_str``: Query string to run. Keywords like ``LIMIT`` and ``OFFSET`` are not allowed. Required.
* ``limit``: Number of returned results per page. By default it is 10.

NoSQL
=====

NoSQL data stores are used for storing arbitrary data without first defining their
structure. To query the supported servers, you must install their drivers using PyPi.

You can search in the following servers:

* `Redis`_
* `MongoDB`_

Redis
-----

Reqired PyPi package: ``redis``

Example configuration:

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

Available options
~~~~~~~~~~~~~~~~~

* ``host``: IP address of the host running Redis. By default it is ``127.0.0.1``.
* ``port``: Port number Redis is listening on. By default it is ``6379``.
* ``password``: Password if required by Redis.
* ``db``: Number of the database you are connecting to.
* ``exact_match_only``: Enable if you need exact matching. By default it is ``True``.


MongoDB
-------

Required PyPi package: ``pymongo``

Below is an example configuration for using a MongoDB collection:

.. code:: yaml

  - name : mymongo
    engine : mongodb
    shortcut : icm
    host : '127.0.0.1'
    port : 27017
    database : personal
    collection : income
    key : month
    enable_http: True


Available options
~~~~~~~~~~~~~~~~~

* ``host``: IP address of the host running MongoDB. By default it is ``127.0.0.1``.
* ``port``: Port number MongoDB is listening on. By default it is ``27017``.
* ``password``: Password if required by Redis.
* ``database``: Name of the database you are connecting to.
* ``collection``: Name of the collection you want to search in.
* ``exact_match_only``: Enable if you need exact matching. By default it is ``True``.
