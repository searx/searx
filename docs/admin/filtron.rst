==========================
How to protect an instance
==========================

.. _filtron: https://github.com/asciimoo/filtron

Searx depens on external search services.  To avoid the abuse of these services
it is advised to limit the number of requests processed by searx.

An application firewall, filtron_ solves exactly this problem.  Filtron is just
a middleware between your web server (nginx, apache, ...) and searx.


filtron & go
============

.. _Go: https://golang.org/
.. _filtron README: https://github.com/asciimoo/filtron/blob/master/README.md


.. sidebar:: init system

   ATM the ``filtron.sh`` supports only systemd init process used by debian,
   ubuntu and many other dists.  If you have a working init.d file to start/stop
   filtron service, please contribute.

Filtron needs Go_ installed.  If Go_ is preinstalled, filtron_ is simply
installed by ``go get`` package management (see `filtron README`_).  If you use
filtron as middleware, a more isolated setup is recommended.

#. Create a separated user account (``filtron``).
#. Download and install Go_ binary in users $HOME (``~filtron``).
#. Install filtron with the package management of Go_ (``go get -v -u
   github.com/asciimoo/filtron``)
#. Setup a proper rule configuration :origin:`[ref]
   <utils/templates/etc/filtron/rules.json>` (``/etc/filtron/rules.json``).
#. Setup a systemd service unit :origin:`[ref]
   <utils/templates/lib/systemd/system/filtron.service>`
   (``/lib/systemd/system/filtron.service``).

To simplify such a installation and the maintenance of; use our script
``utils/filtron.sh``:

.. program-output:: ../utils/filtron.sh --help
   :ellipsis: 0,5


Sample configuration of filtron
===============================

An example configuration can be find below. This configuration limits the access
of:

- scripts or applications (roboagent limit)
- webcrawlers (botlimit)
- IPs which send too many requests (IP limit)
- too many json, csv, etc. requests (rss/json limit)
- the same UserAgent of if too many requests (useragent limit)

.. code:: json

   [{
      "name":"search request",
      "filters":[
         "Param:q",
         "Path=^(/|/search)$"
      ],
      "interval":"<time-interval-in-sec (int)>",
      "limit":"<max-request-number-in-interval (int)>",
      "subrules":[
         {
            "name":"roboagent limit",
            "interval":"<time-interval-in-sec (int)>",
            "limit":"<max-request-number-in-interval (int)>",
            "filters":[
               "Header:User-Agent=(curl|cURL|Wget|python-requests|Scrapy|FeedFetcher|Go-http-client)"
            ],
            "actions":[
               {
                  "name":"block",
                  "params":{
                     "message":"Rate limit exceeded"
                  }
               }
            ]
         },
         {
            "name":"botlimit",
            "limit":0,
            "stop":true,
            "filters":[
               "Header:User-Agent=(Googlebot|bingbot|Baiduspider|yacybot|YandexMobileBot|YandexBot|Yahoo! Slurp|MJ12bot|AhrefsBot|archive.org_bot|msnbot|MJ12bot|SeznamBot|linkdexbot|Netvibes|SMTBot|zgrab|James BOT)"
            ],
            "actions":[
               {
                  "name":"block",
                  "params":{
                     "message":"Rate limit exceeded"
                  }
               }
            ]
         },
         {
            "name":"IP limit",
            "interval":"<time-interval-in-sec (int)>",
            "limit":"<max-request-number-in-interval (int)>",
            "stop":true,
            "aggregations":[
               "Header:X-Forwarded-For"
            ],
            "actions":[
               {
                  "name":"block",
                  "params":{
                     "message":"Rate limit exceeded"
                  }
               }
            ]
         },
         {
            "name":"rss/json limit",
            "interval":"<time-interval-in-sec (int)>",
            "limit":"<max-request-number-in-interval (int)>",
            "stop":true,
            "filters":[
               "Param:format=(csv|json|rss)"
            ],
            "actions":[
               {
                  "name":"block",
                  "params":{
                     "message":"Rate limit exceeded"
                  }
               }
            ]
         },
         {
            "name":"useragent limit",
            "interval":"<time-interval-in-sec (int)>",
            "limit":"<max-request-number-in-interval (int)>",
            "aggregations":[
               "Header:User-Agent"
            ],
            "actions":[
               {
                  "name":"block",
                  "params":{
                     "message":"Rate limit exceeded"
                  }
               }
            ]
         }
      ]
   }]



Route request through filtron
=============================

Filtron can be started using the following command:

.. code:: sh

   $ filtron -rules rules.json

It listens on ``127.0.0.1:4004`` and forwards filtered requests to
``127.0.0.1:8888`` by default.

Use it along with ``nginx`` with the following example configuration.

.. code:: nginx

   location / {
        proxy_set_header   Host    $http_host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Scheme $scheme;
        proxy_pass         http://127.0.0.1:4004/;
   }

Requests are coming from port 4004 going through filtron and then forwarded to
port 8888 where a searx is being run.
