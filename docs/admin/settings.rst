.. _settings.yml:

================
``settings.yml``
================

This page describe the options possibilities of the :origin:`searx/settings.yml`
file.

.. sidebar:: Further reading ..

   - :ref:`use_default_settings.yml`
   - :ref:`search API`

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. _settings location:

settings.yml location
=====================

First, searx will try to load settings.yml from these locations:

1. the full path specified in the ``SEARX_SETTINGS_PATH`` environment variable.
2. ``/etc/searx/settings.yml``

If these files don't exist (or are empty or can't be read), searx uses the
:origin:`searx/settings.yml` file.


.. _settings global:

Global Settings
===============

``general:``
------------

.. code:: yaml

   general:
       debug : False # Debug mode, only for development
       instance_name : "searx" # displayed name
       git_url: https://github.com/searx/searx
       git_branch: master
       issue_url: https://github.com/searx/searx/issues
       docs_url: https://searx.github.io/searx
       public_instances: https://searx.space
       contact_url: False # mailto:contact@example.com
       wiki_url: https://github.com/searx/searx/wiki
       twitter_url: https://twitter.com/Searx_engine

``debug`` :
  Allow a more detailed log if you run searx directly. Display *detailed* error
  messages in the browser too, so this must be deactivated in production.

``contact_url``:
  Contact ``mailto:`` address or WEB form.

``git_url`` and ``git_branch``:
  Changes this, to point to your searx fork (branch).

``docs_url``
  If you host your own documentation, change this URL.

``wiki_url``:
  Link to your wiki (or ``False``)

``twitter_url``:
  Link to your tweets (or ``False``)


``server:``
-----------

.. code:: yaml

   server:
       port : 8888
       bind_address : "127.0.0.1"      # address to listen on
       secret_key : "ultrasecretkey"   # change this!
       base_url : False                # set custom base_url (or False)
       image_proxy : False             # proxying image results through searx
       default_locale : ""             # default interface locale
       default_theme : oscar           # ui theme
       default_http_headers:
           X-Content-Type-Options : nosniff
           X-XSS-Protection : 1; mode=block
           X-Download-Options : noopen
           X-Robots-Tag : noindex, nofollow
           Referrer-Policy : no-referrer

``port`` & ``bind_address``:
  Port number and *bind address* of the searx web application if you run it
  directly using ``python searx/webapp.py``.  Doesn't apply to searx running on
  Apache or Nginx.

``secret_key`` :
  Used for cryptography purpose.

``base_url`` :
  The base URL where searx is deployed.  Used to create correct inbound links.

``image_proxy`` :
  Allow your instance of searx of being able to proxy images.  Uses memory space.

``default_locale`` :
  Searx interface language.  If blank, the locale is detected by using the
  browser language.  If it doesn't work, or you are deploying a language
  specific instance of searx, a locale can be defined using an ISO language
  code, like ``fr``, ``en``, ``de``.

``default_theme`` :
  Name of the theme you want to use by default on your searx instance.

.. _HTTP headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers

``default_http_headers``:
  Set additional HTTP headers, see `#755 <https://github.com/searx/searx/issues/715>`__

``outgoing:``
-------------

.. code:: yaml

   outgoing: # communication with search engines
       request_timeout : 2.0        # default timeout in seconds, can be override by engine
       # max_request_timeout: 10.0  # the maximum timeout in seconds
       useragent_suffix : ""        # informations like an email address to the administrator
       pool_connections : 100       # Number of different hosts
       pool_maxsize : 10            # Number of simultaneous requests by host
   # uncomment below section if you want to use a proxy
   #    proxies:
   #        http:
   #            - http://proxy1:8080
   #            - http://proxy2:8080
   #        https:
   #            - http://proxy1:8080
   #            - http://proxy2:8080
   # uncomment below section only if you have more than one network interface
   # which can be the source of outgoing search requests
   #    source_ips:
   #        - 1.1.1.1
   #        - 1.1.1.2


``request_timeout`` :
  Global timeout of the requests made to others engines in seconds.  A bigger
  timeout will allow to wait for answers from slow engines, but in consequence
  will slow searx reactivity (the result page may take the time specified in the
  timeout to load). Can be override by :ref:`settings engine`

``useragent_suffix`` :
  Suffix to the user-agent searx uses to send requests to others engines.  If an
  engine wish to block you, a contact info here may be useful to avoid that.

.. _requests proxies: https://requests.readthedocs.io/en/latest/user/advanced/#proxies
.. _PySocks: https://pypi.org/project/PySocks/

``proxies`` :
  Define one or more proxies you wish to use, see `requests proxies`_.
  If there are more than one proxy for one protocol (http, https),
  requests to the engines are distributed in a round-robin fashion.

  - Proxy: `see <https://2.python-requests.org/en/latest/user/advanced/#proxies>`__.
  - SOCKS proxies are also supported: `see <https://2.python-requests.org/en/latest/user/advanced/#socks>`__

``source_ips`` :
  If you use multiple network interfaces, define from which IP the requests must
  be made. This parameter is ignored when ``proxies`` is set.


``locales:``
------------

.. code:: yaml

   locales:
       en : English
       de : Deutsch
       he : Hebrew
       hu : Magyar
       fr : Français
       es : Español
       it : Italiano
       nl : Nederlands
       ja : 日本語 (Japanese)
       tr : Türkçe
       ru : Russian
       ro : Romanian

``locales`` :
  Locales codes and their names.  Available translations of searx interface.


.. _settings engine:

Engine settings
===============

.. sidebar:: Further reading ..

   - :ref:`engines-dev`

.. code:: yaml

   - name : bing
     engine : bing
     shortcut : bi
     base_url : 'https://{language}.wikipedia.org/'
     categories : general
     timeout : 3.0
     api_key : 'apikey'
     disabled : True
     language : en_US
     #proxies:
     #    http:
     #        - http://proxy1:8080
     #        - http://proxy2:8080
     #    https:
     #        - http://proxy1:8080
     #        - http://proxy2:8080
     #        - socks5://user:password@proxy3:1080
     #        - socks5h://user:password@proxy4:1080

``name`` :
  Name that will be used across searx to define this engine.  In settings, on
  the result page...

``engine`` :
  Name of the python file used to handle requests and responses to and from this
  search engine.

``shortcut`` :
  Code used to execute bang requests (in this case using ``!bi`` or ``?bi``)

``base_url`` : optional
  Part of the URL that should be stable across every request.  Can be useful to
  use multiple sites using only one engine, or updating the site URL without
  touching at the code.

``categories`` : optional
  Define in which categories this engine will be active.  Most of the time, it is
  defined in the code of the engine, but in a few cases it is useful, like when
  describing multiple search engine using the same code.

``timeout`` : optional
  Timeout of the search with the current search engine.  **Be careful, it will
  modify the global timeout of searx.**

``api_key`` : optional
  In a few cases, using an API needs the use of a secret key.  How to obtain them
  is described in the file.

``disabled`` : optional
  To disable by default the engine, but not deleting it.  It will allow the user
  to manually activate it in the settings.

``language`` : optional
  If you want to use another language for a specific engine, you can define it
  by using the full ISO code of language and country, like ``fr_FR``, ``en_US``,
  ``de_DE``.

``weigth`` : default ``1``
  Weighting of the results of this engine.

``display_error_messages`` : default ``True``
  When an engine returns an error, the message is displayed on the user interface.

.. note::

   A few more options are possible, but they are pretty specific to some
   engines, and so won't be described here.


.. _settings use_default_settings:

use_default_settings
====================

.. sidebar:: ``use_default_settings: True``

   - :ref:`settings location`
   - :ref:`use_default_settings.yml`
   - :origin:`/etc/searx/settings.yml <utils/templates/etc/searx/use_default_settings.yml>`

The user defined ``settings.yml`` is loaded from the :ref:`settings location`
and can relied on the default configuration :origin:`searx/settings.yml` using:

 ``use_default_settings: True``

``server:``
  In the following example, the actual settings are the default settings defined
  in :origin:`searx/settings.yml` with the exception of the ``secret_key`` and
  the ``bind_address``:

  .. code-block:: yaml

    use_default_settings: True
    server:
        secret_key: "uvys6bRhKHUdFF5CqbJonSDSRN8H0sCBziNSrDGNVdpz7IeZhveVart3yvghoKHA"
        bind_address: "0.0.0.0"

``engines:``
  With ``use_default_settings: True``, each settings can be override in a
  similar way, the ``engines`` section is merged according to the engine
  ``name``.  In this example, searx will load all the engine and the arch linux
  wiki engine has a :ref:`token<private engines>`:

  .. code-block:: yaml

    use_default_settings: True
    server:
        secret_key: "uvys6bRhKHUdFF5CqbJonSDSRN8H0sCBziNSrDGNVdpz7IeZhveVart3yvghoKHA"
    engines:
      - name: arch linux wiki
        tokens: ['$ecretValue']

``engines:`` / ``remove:``
  It is possible to remove some engines from the default settings. The following
  example is similar to the above one, but searx doesn't load the the google
  engine:

  .. code-block:: yaml

    use_default_settings:
        engines:
           remove:
             - google
    server:
        secret_key: "uvys6bRhKHUdFF5CqbJonSDSRN8H0sCBziNSrDGNVdpz7IeZhveVart3yvghoKHA"
    engines:
      - name: arch linux wiki
        tokens: ['$ecretValue']

``engines:`` / ``keep_only:``
  As an alternative, it is possible to specify the engines to keep. In the
  following example, searx has only two engines:

  .. code-block:: yaml

    use_default_settings:
        engines:
           keep_only:
             - google
             - duckduckgo
    server:
        secret_key: "uvys6bRhKHUdFF5CqbJonSDSRN8H0sCBziNSrDGNVdpz7IeZhveVart3yvghoKHA"
    engines:
      - name: google
        tokens: ['$ecretValue']
      - name: duckduckgo
        tokens: ['$ecretValue']
