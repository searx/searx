=================
Query SQL servers 
=================

Now you can query SQL servers using searx. The following ones are supported:

* `PostgreSQL`_
* `MySQL`_
* `SQLite`_

All of the engines above are added to ``settings.yml`` just commented out, as you have to
set the required attributes for the engines, e.g. ``database``. By default, the engines use
``key-value`` template for displaying results. If you are not satisfied with the original result layout,
you can use your owm template by placing the template under
``searx/templates/{theme_name}/result_templates/{template_name}`` and setting
``result_template`` attribute to ``{template_name}``.

As mentioned in previous blog posts, if you do not wish to expose these engines on a
public instance, you can still add them and limit the access by setting ``tokens``
as described in the `blog post about private engines`_.

Configure the engines
=====================

The configuration of the new database engines are similar. You must put a valid
SELECT SQL query in ``query_str``. At the moment you can only bind at most
one parameter in your query. By setting the attribute ``limit`` you can
define how many results you want from the SQL server. Basically, it
is the same as the LIMIT keyword in SQL.

Please, do not include LIMIT or OFFSET in your SQL query as the engines
rely on these keywords during paging. If you want to configure the number of returned results
use the option ``limit``.

PostgreSQL
----------

PostgreSQL is a powerful and robust open source database.

Before configuring the PostgreSQL engine, you must install the dependency ``psychopg2``.

You can find an example configuration below:

.. code:: yaml

  - name : postgresql
    engine : postgresql
    database : my_database
    username : searx
    password : password
    query_str : 'SELECT * from my_table WHERE my_column = %(query)s'
    shortcut : psql


MySQL
-----

MySQL is said to be the most popular open source database. 

Before enabling MySQL engine, you must install the package ``mysql-connector-python``.

The authentication plugin is configurable by setting ``auth_plugin`` in the attributes.
By default it is set to ``caching_sha2_password``.

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


SQLite
------

SQLite is a small, fast and reliable SQL database engine. It does not require
any extra dependency.

You can read from your database ``my_database`` using this example configuration:

.. code:: yaml

  - name : sqlite
    engine : sqlite
    shortcut: sq
    database : my_database
    query_str : 'SELECT * FROM my_table WHERE my_column=:query'


Next steps
==========

The next step is to add support for more data stores, e.g. Redis and MongoDB.

Acknowledgement
===============

This development was sponsored by `Search and Discovery Fund`_ of `NLnet Foundation`_ .

.. _PostgreSQL: https://www.postgresql.org/
.. _MySQL: https://www.mysql.com/
.. _SQLite: https://www.sqlite.org/index.html
.. _blog post about private engines: private-engines.html#private-engines
.. _Search and Discovery Fund: https://nlnet.nl/discovery
.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2021.05.23 23:16


