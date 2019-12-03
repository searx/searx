How to setup result proxy
=========================

By default searx can only act as an image proxy for result images,
but it is possible to proxify all the result URLs with an external service,
`morty <https://github.com/asciimoo/morty>`__.

To use this feature, morty has to be installed and activated in searx's ``settings.yml``.

Add the following snippet to your ``settings.yml`` and restart searx:


.. code:: yaml

    result_proxy:
        url : http://127.0.0.1:3000/
        key : your_morty_proxy_key

``url`` is the address of the running morty service

``key`` is an optional argument, see `morty's README <https://github.com/asciimoo/morty>`__ for more information.
