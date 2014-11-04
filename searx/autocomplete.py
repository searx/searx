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
from requests import get
from json import loads
from urllib import urlencode


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
