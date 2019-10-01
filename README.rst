searx
=====

A privacy-respecting, hackable `metasearch
engine <https://en.wikipedia.org/wiki/Metasearch_engine>`__.

Pronunciation: səːks

List of `running
instances <https://github.com/asciimoo/searx/wiki/Searx-instances>`__.

See the `documentation <https://asciimoo.github.io/searx>`__ and the `wiki <https://github.com/asciimoo/searx/wiki>`__ for more information.

|OpenCollective searx backers|
|OpenCollective searx sponsors|

Installation
~~~~~~~~~~~~

With Docker
------
Go to the `searx-docker <https://github.com/searx/searx-docker>`__ project.

Without Docker
------
For all of the details, follow this `step by step installation <https://asciimoo.github.io/searx/dev/install/installation.html>`__.

Note: the documentation needs to be updated.

If you are in a hurry
------
-  clone the source:
   ``git clone https://github.com/asciimoo/searx.git && cd searx``
-  install dependencies: ``./manage.sh update_packages``
-  edit your
   `settings.yml <https://github.com/asciimoo/searx/blob/master/searx/settings.yml>`__
   (set your ``secret_key``!)
-  run ``python searx/webapp.py`` to start the application


Bugs
~~~~

Bugs or suggestions? Visit the `issue
tracker <https://github.com/asciimoo/searx/issues>`__.

`License <https://github.com/asciimoo/searx/blob/master/LICENSE>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

More about searx
~~~~~~~~~~~~~~~~

-  `openhub <https://www.openhub.net/p/searx/>`__
-  `twitter <https://twitter.com/Searx_engine>`__
-  IRC: #searx @ freenode


.. |OpenCollective searx backers| image:: https://opencollective.com/searx/backers/badge.svg
   :target: https://opencollective.com/searx#backer


.. |OpenCollective searx sponsors| image:: https://opencollective.com/searx/sponsors/badge.svg
   :target: https://opencollective.com/searx#sponsor
