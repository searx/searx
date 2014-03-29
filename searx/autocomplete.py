from lxml import etree
from requests import get
from json import loads


def dbpedia(query):
    # dbpedia autocompleter
    autocomplete_url = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryString={q}'  # noqa

    response = get(autocomplete_url.format(q=query))

    results = []

    if response.ok:
        dom = etree.fromstring(response.content)
        results = dom.xpath('//a:Result/a:Label//text()',
                            namespaces={'a': 'http://lookup.dbpedia.org/'})

    return results


def google(query):
    # google autocompleter
    autocomplete_url = 'http://suggestqueries.google.com/complete/search?client=toolbar&q={q}'  # noqa

    response = get(autocomplete_url.format(q=query))

    results = []

    if response.ok:
        dom = etree.fromstring(response.content)
        results = dom.xpath('//suggestion/@data')

    return results


def wikipedia(query):
    # wikipedia autocompleter
    url = 'https://en.wikipedia.org/w/api.php?action=opensearch&search={q}&limit=10&namespace=0&format=json'  # noqa

    resp = loads(get(url.format(q=query)).text)
    return resp[1]


backends = {'dbpedia': dbpedia,
            'google': google,
            'wikipedia': wikipedia
            }
