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


from lxml import etree
from json import loads
from searx import settings
from searx.languages import language_codes
from searx.engines import (
    categories, engines, engine_shortcuts
)
from searx.poolrequests import get as http_get
from searx.url_utils import urlencode


def get(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = settings['outgoing']['request_timeout']

    return http_get(*args, **kwargs)


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
                    results.append(first_char + '{categorie}'.format(categorie=categorie))

            # check if query starts with engine name
            for engine in engines:
                if engine.startswith(engine_query.replace('_', ' ')):
                    results.append(first_char + '{engine}'.format(engine=engine.replace(' ', '_')))

            # check if query starts with engine shortcut
            for engine_shortcut in engine_shortcuts:
                if engine_shortcut.startswith(engine_query):
                    results.append(first_char + '{engine_shortcut}'.format(engine_shortcut=engine_shortcut))

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
                lang_id, lang_name, country, english_name = map(unicode.lower, lc)

                # check if query starts with language-id
                if lang_id.startswith(engine_query):
                    if len(engine_query) <= 2:
                        results.append(u':{lang_id}'.format(lang_id=lang_id.split('-')[0]))
                    else:
                        results.append(u':{lang_id}'.format(lang_id=lang_id))

                # check if query starts with language name
                if lang_name.startswith(engine_query) or english_name.startswith(engine_query):
                    results.append(u':{lang_name}'.format(lang_name=lang_name))

                # check if query starts with country
                if country.startswith(engine_query.replace('_', ' ')):
                    results.append(u':{country}'.format(country=country.replace(' ', '_')))

    # remove duplicates
    result_set = set(results)

    # remove results which are already contained in the query
    for query_part in full_query.query_parts:
        if query_part in result_set:
            result_set.remove(query_part)

    # convert result_set back to list
    return list(result_set)


def dbpedia(query, lang):
    # dbpedia autocompleter, no HTTPS
    autocomplete_url = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?'

    response = get(autocomplete_url + urlencode(dict(QueryString=query)))

    results = []

    if response.ok:
        dom = etree.fromstring(response.content)
        results = dom.xpath('//a:Result/a:Label//text()',
                            namespaces={'a': 'http://lookup.dbpedia.org/'})

    return results


def duckduckgo(query, lang):
    # duckduckgo autocompleter
    url = 'https://ac.duckduckgo.com/ac/?{0}&type=list'

    resp = loads(get(url.format(urlencode(dict(q=query)))).text)
    if len(resp) > 1:
        return resp[1]
    return []


def google(query, lang):
    # google autocompleter
    autocomplete_url = 'https://suggestqueries.google.com/complete/search?client=toolbar&'

    response = get(autocomplete_url + urlencode(dict(hl=lang, q=query)))

    results = []

    if response.ok:
        dom = etree.fromstring(response.text)
        results = dom.xpath('//suggestion/@data')

    return results


def startpage(query, lang):
    # startpage autocompleter
    url = 'https://startpage.com/do/suggest?{query}'

    resp = get(url.format(query=urlencode({'query': query}))).text.split('\n')
    if len(resp) > 1:
        return resp
    return []


def qwant(query, lang):
    # qwant autocompleter (additional parameter : lang=en_en&count=xxx )
    url = 'https://api.qwant.com/api/suggest?{query}'

    resp = get(url.format(query=urlencode({'q': query, 'lang': lang})))

    results = []

    if resp.ok:
        data = loads(resp.text)
        if data['status'] == 'success':
            for item in data['data']['items']:
                results.append(item['value'])

    return results


def wikipedia(query, lang):
    # wikipedia autocompleter
    url = 'https://' + lang + '.wikipedia.org/w/api.php?action=opensearch&{0}&limit=10&namespace=0&format=json'

    resp = loads(get(url.format(urlencode(dict(search=query)))).text)
    if len(resp) > 1:
        return resp[1]
    return []


backends = {'dbpedia': dbpedia,
            'duckduckgo': duckduckgo,
            'google': google,
            'startpage': startpage,
            'qwant': qwant,
            'wikipedia': wikipedia
            }
