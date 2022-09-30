=================================
Private searx project is finished
=================================

We are officially finished with the Private searx project. The goal was to
extend searx capabilities beyond just searching on the Internet. We added
support for offline engines. These engines do not connect to the Internet,
they find results locally.

As some of the offline engines run commands on the searx host, we added an
option to protect any engine by making them private. Private engines can only be
accessed using a token.

After searx was prepared to run offline queries we added numerous new engines:

1. Command line engine
2. MySQL
3. PostgreSQL
4. SQLite
5. Redis
6. MongoDB

We also added new engines that communicate over HTTP, but you might want to keep
them private:

1. Elasticsearch
2. Meilisearch
3. Solr

The last step was to document this work. We added new tutorials on creating
command engines, making engines private and also adding a custom result template
to your own engines.

Acknowledgement
===============

The project was sponsored by `Search and Discovery Fund`_ of `NLnet
Foundation`_. We would like to thank the NLnet for not only the funds, but the
conversations and their ideas. They were truly invested and passionate about
supporting searx.

.. _Search and Discovery Fund: https://nlnet.nl/discovery
.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2022.09.30 23:15

