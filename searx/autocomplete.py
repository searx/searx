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

    resp = loads(get(url.format(urlencode(dict(q=query)))).text)
    if len(resp) > 1:
        return resp[1]
    return []


backends = {'dbpedia': dbpedia,
            'google': google,
            'wikipedia': wikipedia
            }
