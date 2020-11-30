.. _settings.yml:

================
``settings.yml``
================

This page describe the options possibilities of the :origin:`searx/settings.yml`
file.

.. sidebar:: Further reading ..

   - :ref:`search API`

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. _settings global:

Global Settings
===============

.. code:: yaml

   server:
       port : 8888
       secret_key : "ultrasecretkey" # change this!
       debug : False                 # debug mode, only for development
       request_timeout : 2.0         # seconds
       base_url : False              # set custom base_url (or False)
       themes_path : ""              # custom ui themes path
       default_theme : oscar         # ui theme
       useragent_suffix : ""         # suffix of searx_useragent, could contain
                                     # informations like admins email address
       image_proxy : False           # proxying image results through searx
       default_locale : ""           # default interface locale

   outgoing: # communication with search engines
       request_timeout : 2.0 # default timeout in seconds, can be override by engine
       # max_request_timeout: 10.0 # the maximum timeout in seconds
       useragent_suffix : "" # suffix of searx_useragent, could contain informations like an email address to the administrator
       pool_connections : 100 # Number of different hosts
       pool_maxsize : 10 # Number of simultaneous requests by host

       #proxies:
       #    http:
       #        - http://proxy1:8080
       #        - http://proxy2:8080
       #    https:
       #        - http://proxy1:8080
       #        - http://proxy2:8080
       #        - socks5://user:password@proxy3:1080
       #        - socks5h://user:password@proxy4:1080

       #source_ips:
       #    - 1.1.1.1
       #    - 1.1.1.2

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


``port`` :
  Port number of the searx web application if you run it directly using ``python
  searx/webapp.py``.  Doesn't apply to searx running on Apache or Nginx.

``secret_key`` :
  Used for cryptography purpose.

``debug`` :
  Allow a more detailed log if you run searx directly. Display *detailed* error
  messages in the browser too, so this must be deactivated in production.

``request_timeout`` :
  Global timeout of the requests made to others engines in seconds.  A bigger
  timeout will allow to wait for answers from slow engines, but in consequence
  will slow searx reactivity (the result page may take the time specified in the
  timeout to load)

``base_url`` :
  The base URL where searx is deployed.  Used to create correct inbound links.

``themes_path`` :
  Path to where the themes are located.  If you didn't develop anything, leave it
  blank.

``default_theme`` :
  Name of the theme you want to use by default on your searx instance.

``useragent_suffix`` :
  Suffix to the user-agent searx uses to send requests to others engines.  If an
  engine wish to block you, a contact info here may be useful to avoid that.

``image_proxy`` :
  Allow your instance of searx of being able to proxy images.  Uses memory space.

``default_locale`` :
  Searx interface language.  If blank, the locale is detected by using the
  browser language.  If it doesn't work, or you are deploying a language
  specific instance of searx, a locale can be defined using an ISO language
  code, like ``fr``, ``en``, ``de``.

.. _requests proxies: http://requests.readthedocs.io/en/latest/user/advanced/#proxies
.. _PySocks: https://pypi.org/project/PySocks/

``proxies`` :
  Define one or more proxies you wish to use, see `requests proxies`_.
  If there are more than one proxy for one protocol (http, https),
  requests to the engines are distributed in a round-robin fashion.

``source_ips`` :
  If you use multiple network interfaces, define from which IP the requests must
  be made. This parameter is ignored when ``proxies`` is set.

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
