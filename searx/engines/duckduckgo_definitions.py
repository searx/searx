import json
from urllib import urlencode

url = 'http://api.duckduckgo.com/?{query}&format=json&pretty=0&no_redirect=1'


def request(query, params):
    params['url'] = url.format(query=urlencode({'q': query}))
    return params


def response(resp):
    search_res = json.loads(resp.text)
    results = []
    if 'Definition' in search_res:
        if search_res.get('AbstractURL'):
            res = {'title': search_res.get('Heading', ''),
                   'content': search_res.get('Definition', ''),
                   'url': search_res.get('AbstractURL', ''),
                   'class': 'definition_result'}
            results.append(res)

    return results
