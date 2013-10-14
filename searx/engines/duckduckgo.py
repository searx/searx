from lxml import html


def request(query, params):
    params['method']    = 'POST'
    params['url']       = 'https://duckduckgo.com/html'
    params['data']['q'] = query
    return params


def response(resp):
    dom = html.fromstring(resp.text)
    results = dom.xpath('//div[@class="results_links results_links_deep web-result"]')
    return [html.tostring(x) for x in results]
