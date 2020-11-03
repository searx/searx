==================================
Limit access to your searx engines
==================================

Administrators might find themselves wanting to limit access to some of the
enabled engines on their instances. It might be because they do not want to
expose some private information through an offline engine. Or they
would rather share engines only with their trusted friends or colleagues.

.. _private engines:

Private engines
===============

To solve this issue private engines were introduced in :pull:`1823`.
A new option was added to engines named `tokens`. It expects a list
of strings. If the user making a request presents one of the tokens
of an engine, they can access information about the engine
and make search requests.

Example configuration to restrict access to the Arch Linux Wiki engine:

.. code:: yaml

  - name : arch linux wiki
    engine : archlinux
    shortcut : al
    tokens : [ 'my-secret-token' ]


Unless a user has configured the right token, the engine is going
to be hidden from him/her. It is not going to be included in the 
list of engines on the Preferences page and in the output of
`/config` REST API call.

Tokens can be added to one's configuration on the Preferences page
under "Engine tokens". The input expects a comma separated list of
strings.

The distribution of the tokens from the administrator to the users
is not carved in stone. As providing access to such engines
implies that the admin knows and trusts the user, we do not see
necessary to come up with a strict process. Instead,
we would like to add guidelines to the documentation of the feature.
 
Next steps
==========

Now that searx has support for both offline engines and private engines,
it is possible to add concrete engines which benefit from these features.
For example engines which search on the local host running the instance.
Be it searching your file system or querying a private database. Be creative
and come up with new solutions which fit your use case.

Acknowledgement
===============

This development was sponsored by `Search and Discovery Fund`_ of `NLnet Foundation`_ .

.. _Search and Discovery Fund: https://nlnet.nl/discovery
.. _NLnet Foundation: https://nlnet.nl/


| Happy hacking.
| kvch // 2020.02.28 22:26
