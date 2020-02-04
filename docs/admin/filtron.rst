
.. _searx_filtron:

==========================
How to protect an instance
==========================

.. sidebar:: further reading

   - :ref:`filtron.sh`

.. contents:: Contents
   :depth: 2
   :local:
   :backlinks: entry

.. _filtron: https://github.com/asciimoo/filtron

Searx depens on external search services.  To avoid the abuse of these services
it is advised to limit the number of requests processed by searx.

An application firewall, filtron_ solves exactly this problem.  Filtron is just
a middleware between your web server (nginx, apache, ...) and searx, we describe
such infratructures in chapter: :ref:`architecture`.


filtron & go
============

.. _Go: https://golang.org/
.. _filtron README: https://github.com/asciimoo/filtron/blob/master/README.md

Filtron needs Go_ installed.  If Go_ is preinstalled, filtron_ is simply
installed by ``go get`` package management (see `filtron README`_).  If you use
filtron as middleware, a more isolated setup is recommended.  To simplify such
an installation and the maintenance of, use our script :ref:`filtron.sh`.


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
