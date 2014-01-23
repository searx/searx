from json import loads
from urllib import urlencode
from searx.utils import html_to_text

url = 'https://duckduckgo.com/'
search_url = url + 'd.js?{query}&p=1&s=0'
locale = 'us-en'


def request(query, params):
    q = urlencode({'q': query,
                   'l': locale})
    params['url'] = search_url.format(query=q)
    return params


def response(resp):
    results = []
    search_res = loads(resp.text[resp.text.find('[{'):-2])[:-1]
    for r in search_res:
        if not r.get('t'):
            continue
        results.append({'title': r['t'],
                       'content': html_to_text(r['a']),
                       'url': r['u']})
    return results
