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
from urllib.parse import urlencode

from httpx import HTTPError


from searx import settings
from searx.network import get as http_get
from searx.exceptions import SearxEngineResponseException


def get(*args, **kwargs):
    if 'timeout' not in kwargs:
        kwargs['timeout'] = settings['outgoing']['request_timeout']
    kwargs['raise_for_httperror'] = True
    return http_get(*args, **kwargs)


def dbpedia(query, lang):
    # dbpedia autocompleter, no HTTPS
    autocomplete_url = 'https://lookup.dbpedia.org/api/search.asmx/KeywordSearch?'

    response = get(autocomplete_url + urlencode(dict(QueryString=query)))

    results = []

    if response.ok:
        dom = etree.fromstring(response.content)
        results = dom.xpath('//Result/Label//text()')

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


def swisscows(query, lang):
    # swisscows autocompleter
    url = 'https://swisscows.ch/api/suggest?{query}&itemsCount=5'

    resp = loads(get(url.format(query=urlencode({'query': query}))).text)
    return resp


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
            'swisscows': swisscows,
            'qwant': qwant,
            'wikipedia': wikipedia
            }


def search_autocomplete(backend_name, query, lang):
    backend = backends.get(backend_name)
    if backend is None:
        return []

    try:
        return backend(query, lang)
    except (HTTPError, SearxEngineResponseException):
        return []
