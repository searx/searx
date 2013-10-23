from json import loads
from urllib import urlencode

url = 'https://duckduckgo.com/'
search_url = url + 'd.js?{query}&l=us-en&p=1&s=0'

def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    search_res = loads(resp.text[resp.text.find('[{'):-2])[:-1]
    for r in search_res:
        if not r.get('t'):
            continue
        results.append({'title': r['t']
                       ,'content': r['a']
                       ,'url': r['u']
                       })
    return results
