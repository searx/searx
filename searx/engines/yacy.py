from json import loads
from urllib import urlencode

url = 'http://localhost:8090'
search_url = '/yacysearch.json?{query}&maximumRecords=10'


def request(query, params):
    params['url'] = url + search_url.format(query=urlencode({'query': query}))
    return params


def response(resp):
    raw_search_results = loads(resp.text)

    if not len(raw_search_results):
        return []

    search_results = raw_search_results.get('channels', {})[0].get('items', [])

    results = []

    for result in search_results:
        tmp_result = {}
        tmp_result['title'] = result['title']
        tmp_result['url'] = result['link']
        tmp_result['content'] = ''

        if len(result['description']):
            tmp_result['content'] += result['description'] + "<br/>"

        if len(result['pubDate']):
            tmp_result['content'] += result['pubDate'] + "<br/>"

        if result['size'] != '-1':
            tmp_result['content'] += result['sizename']

        results.append(tmp_result)

    return results
