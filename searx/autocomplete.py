'''
searx is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

searx is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with searx. If not, see < http://www.gnu.org/licenses/ >.

(C) 2013- by Adam Tauber, <asciimoo@gmail.com>
'''
from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import map


from lxml import etree
from json import loads
from urllib.parse import urlencode
from searx.languages import language_codes
from searx.engines import (
    categories, engines, engine_shortcuts
)
from searx.poolrequests import get
from six.moves import map


def searx_bang(full_query):
    '''check if the searchQuery contain a bang, and create fitting autocompleter results'''
    # check if there is a query which can be parsed
    if len(full_query.getSearchQuery()) == 0:
        return []

    results = []

    # check if current query stats with !bang
    first_char = full_query.getSearchQuery()[0]
    if first_char == '!' or first_char == '?':
        if len(full_query.getSearchQuery()) == 1:
            # show some example queries
            # TODO, check if engine is not avaliable
            results.append(first_char + "images")
            results.append(first_char + "wikipedia")
            results.append(first_char + "osm")
        else:
            engine_query = full_query.getSearchQuery()[1:]

            # check if query starts with categorie name
            for categorie in categories:
                if categorie.startswith(engine_query):
                    results.append(first_char+'{categorie}'.format(categorie=categorie))

            # check if query starts with engine name
            for engine in engines:
                if engine.startswith(engine_query.replace('_', ' ')):
                    results.append(first_char+'{engine}'.format(engine=engine.replace(' ', '_')))

            # check if query starts with engine shortcut
            for engine_shortcut in engine_shortcuts:
                if engine_shortcut.startswith(engine_query):
                    results.append(first_char+'{engine_shortcut}'.format(engine_shortcut=engine_shortcut))

    # check if current query stats with :bang
    elif first_char == ':':
        if len(full_query.getSearchQuery()) == 1:
            # show some example queries
            results.append(":en")
            results.append(":en_us")
            results.append(":english")
            results.append(":united_kingdom")
        else:
            engine_query = full_query.getSearchQuery()[1:]

            for lc in language_codes:
                lang_id, lang_name, country = list(map(str.lower, lc))

                # check if query starts with language-id
                if lang_id.startswith(engine_query):
                    if len(engine_query) <= 2:
                        results.append(':{lang_id}'.format(lang_id=lang_id.split('_')[0]))
                    else:
                        results.append(':{lang_id}'.format(lang_id=lang_id))

                # check if query starts with language name
                if lang_name.startswith(engine_query):
                    results.append(':{lang_name}'.format(lang_name=lang_name))

                # check if query starts with country
                if country.startswith(engine_query.replace('_', ' ')):
                    results.append(':{country}'.format(country=country.replace(' ', '_')))

    # remove duplicates
    result_set = set(results)

    # remove results which are already contained in the query
    for query_part in full_query.query_parts:
        if query_part in result_set:
            result_set.remove(query_part)

    # convert result_set back to list
    return list(result_set)


def dbpedia(query):
    # dbpedia autocompleter
    autocomplete_url = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?'  # noqa

    response = get(autocomplete_url
                   + urlencode(dict(QueryString=query)))

    results = []

    if response.ok:
        dom = etree.fromstring(response.content)
        results = dom.xpath('//a:Result/a:Label//text()',
                            namespaces={'a': 'http://lookup.dbpedia.org/'})

    return results


def duckduckgo(query):
    # duckduckgo autocompleter
    url = 'https://ac.duckduckgo.com/ac/?{0}&type=list'

    resp = loads(get(url.format(urlencode(dict(q=query)))).text)
    if len(resp) > 1:
        return resp[1]
    return []


def google(query):
    # google autocompleter
    autocomplete_url = 'http://suggestqueries.google.com/complete/search?client=toolbar&'  # noqa

    response = get(autocomplete_url
                   + urlencode(dict(q=query)))

    results = []

    if response.ok:
        dom = etree.fromstring(response.text)
        results = dom.xpath('//suggestion/@data')

    return results


def wikipedia(query):
    # wikipedia autocompleter
    url = 'https://en.wikipedia.org/w/api.php?action=opensearch&{0}&limit=10&namespace=0&format=json'  # noqa

    resp = loads(get(url.format(urlencode(dict(search=query)))).text)
    if len(resp) > 1:
        return resp[1]
    return []


backends = {'dbpedia': dbpedia,
            'duckduckgo': duckduckgo,
            'google': google,
            'wikipedia': wikipedia
            }
