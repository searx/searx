from json import loads


def request(query, params):
    params['url'] = 'https://duckduckgo.com/d.js?q=%s&l=us-en&p=1&s=0' % query
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
