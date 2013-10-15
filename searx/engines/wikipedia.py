from json import loads

def request(query, params):
    params['url'] = 'http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&srprop=timestamp&format=json' % query

    return params


def response(resp):
    search_results = loads(resp.text)
    results = []
    for res in search_results.get('query', {}).get('search', []):
        results.append({'url': 'https://en.wikipedia.org/wiki/%s' % res['title'], 'title': res['title']})
    return results

