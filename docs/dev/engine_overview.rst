
.. _engines-dev:

===============
Engine overview
===============

.. _metasearch-engine: https://en.wikipedia.org/wiki/Metasearch_engine

searx is a metasearch-engine_, so it uses different search engines to provide
better results.

Because there is no general search API which could be used for every search
engine, an adapter has to be built between searx and the external search
engines.  Adapters are stored under the folder :origin:`searx/engines`.

.. contents::
   :depth: 3
   :backlinks: entry


.. _general engine configuration:

general engine configuration
============================

It is required to tell searx the type of results the engine provides. The
arguments can be set in the engine file or in the settings file
(normally ``settings.yml``). The arguments in the settings file override
the ones in the engine file.

It does not matter if an option is stored in the engine file or in the
settings.  However, the standard way is the following:

.. _engine file:

engine file
-----------

======================= =========== ========================================================
argument                type        information
======================= =========== ========================================================
categories              list        pages, in which the engine is working
paging                  boolean     support multible pages
time_range_support      boolean     support search time range
engine_type             str         ``online`` by default, other possibles values are 
                                    ``offline``, ``online_dictionnary``, ``online_currency``
======================= =========== ========================================================

.. _engine settings:

settings.yml
------------

======================= =========== =============================================
argument                type        information
======================= =========== =============================================
name                    string      name of search-engine
engine                  string      name of searx-engine
                                    (filename without ``.py``)
enable_http             bool        enable HTTP
                                    (by default only HTTPS is enabled).
shortcut                string      shortcut of search-engine
timeout                 string      specific timeout for search-engine
display_error_messages  boolean     display error messages on the web UI
proxies                 dict        set proxies for a specific engine
                                    (e.g. ``proxies : {http: socks5://proxy:port,
                                    https: socks5://proxy:port}``)
======================= =========== =============================================


overrides
---------

A few of the options have default values in the engine, but are often
overwritten by the settings.  If ``None`` is assigned to an option in the engine
file, it has to be redefined in the settings, otherwise searx will not start
with that engine.

The naming of overrides is arbitrary.  But the recommended overrides are the
following:

======================= =========== ===========================================
argument                type        information
======================= =========== ===========================================
base_url                string      base-url, can be overwritten to use same
                                    engine on other URL
number_of_results       int         maximum number of results per request
language                string      ISO code of language and country like en_US
api_key                 string      api-key if required by engine
======================= =========== ===========================================

example code
------------

.. code:: python

   # engine dependent config
   categories = ['general']
   paging = True


making a request
================

To perform a search an URL have to be specified.  In addition to specifying an
URL, arguments can be passed to the query.

passed arguments
----------------

These arguments can be used to construct the search query.  Furthermore,
parameters with default value can be redefined for special purposes.

If the ``engine_type`` is ``online```:

====================== ============== ========================================================================
argument               type           default-value, information
====================== ============== ========================================================================
url                    str            ``''``
method                 str            ``'GET'``
headers                set            ``{}``
data                   set            ``{}``
cookies                set            ``{}``
verify                 bool           ``True``
headers.User-Agent     str            a random User-Agent
category               str            current category, like ``'general'``
safesearch             int            ``0``, between ``0`` and ``2`` (normal, moderate, strict)
time_range             Optional[str]  ``None``, can be ``day``, ``week``, ``month``, ``year``
pageno                 int            current pagenumber
language               str            specific language code like ``'en_US'``, or ``'all'`` if unspecified
====================== ============== ========================================================================


If the ``engine_type`` is ``online_dictionnary```, in addition to the ``online`` arguments:

====================== ============ ========================================================================
argument               type         default-value, information
====================== ============ ========================================================================
from_lang              str          specific language code like ``'en_US'``
to_lang                str          specific language code like ``'en_US'``
query                  str          the text query without the languages
====================== ============ ========================================================================

If the ``engine_type`` is ``online_currency```, in addition to the ``online`` arguments:

====================== ============ ========================================================================
argument               type         default-value, information
====================== ============ ========================================================================
amount                 float        the amount to convert
from                   str          ISO 4217 code
to                     str          ISO 4217 code
from_name              str          currency name
to_name                str          currency name
====================== ============ ========================================================================


parsed arguments
----------------

The function ``def request(query, params):`` always returns the ``params``
variable.  Inside searx, the following paramters can be used to specify a search
request:

=================== =========== ==========================================================================
argument            type        information
=================== =========== ==========================================================================
url                 str         requested url
method              str         HTTP request method
headers             set         HTTP header information
data                set         HTTP data information
cookies             set         HTTP cookies
verify              bool        Performing SSL-Validity check
allow_redirects     bool        Follow redirects
max_redirects       int         maximum redirects, hard limit
soft_max_redirects  int         maximum redirects, soft limit. Record an error but don't stop the engine
raise_for_httperror bool        True by default: raise an exception if the HTTP code of response is >= 300
=================== =========== ==========================================================================


example code
------------

.. code:: python

   # search-url
   base_url = 'https://example.com/'
   search_string = 'search?{query}&page={page}'

   # do search-request
   def request(query, params):
       search_path = search_string.format(
           query=urlencode({'q': query}),
           page=params['pageno'])

       params['url'] = base_url + search_path

       return params


returned results
================

Searx is able to return results of different media-types.  Currently the
following media-types are supported:

- default_
- images_
- videos_
- torrent_
- map_

To set another media-type as default, the parameter ``template`` must be set to
the desired type.

default
-------

========================= =====================================================
result-parameter          information
========================= =====================================================
url                       string, url of the result
title                     string, title of the result
content                   string, general result-text
publishedDate             :py:class:`datetime.datetime`, time of publish
========================= =====================================================

images
------

To use this template, the parameter:

========================= =====================================================
result-parameter          information
========================= =====================================================
template                  is set to ``images.html``
url                       string, url to the result site
title                     string, title of the result *(partly implemented)*
content                   *(partly implemented)*
publishedDate             :py:class:`datetime.datetime`,
                          time of publish *(partly implemented)*
img\_src                  string, url to the result image
thumbnail\_src            string, url to a small-preview image
========================= =====================================================

videos
------

========================= =====================================================
result-parameter          information
========================= =====================================================
template                  is set to ``videos.html``
url                       string, url of the result
title                     string, title of the result
content                   *(not implemented yet)*
publishedDate             :py:class:`datetime.datetime`, time of publish
thumbnail                 string, url to a small-preview image
========================= =====================================================

torrent
-------

.. _magnetlink: https://en.wikipedia.org/wiki/Magnet_URI_scheme

========================= =====================================================
result-parameter          information
========================= =====================================================
template                  is set to ``torrent.html``
url                       string, url of the result
title                     string, title of the result
content                   string, general result-text
publishedDate             :py:class:`datetime.datetime`,
                          time of publish *(not implemented yet)*
seed                      int, number of seeder
leech                     int, number of leecher
filesize                  int, size of file in bytes
files                     int, number of files
magnetlink                string, magnetlink_ of the result
torrentfile               string, torrentfile of the result
========================= =====================================================


map
---

========================= =====================================================
result-parameter          information
========================= =====================================================
url                       string, url of the result
title                     string, title of the result
content                   string, general result-text
publishedDate             :py:class:`datetime.datetime`, time of publish
latitude                  latitude of result (in decimal format)
longitude                 longitude of result (in decimal format)
boundingbox               boundingbox of result (array of 4. values
                          ``[lat-min, lat-max, lon-min, lon-max]``)
geojson                   geojson of result (https://geojson.org/)
osm.type                  type of osm-object (if OSM-Result)
osm.id                    id of osm-object (if OSM-Result)
address.name              name of object
address.road              street name of object
address.house_number      house number of object
address.locality          city, place of object
address.postcode          postcode of object
address.country           country of object
========================= =====================================================
