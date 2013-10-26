from json import loads

def request(query, params):
    params['url'] = 'http://127.0.0.1:8888/lsearch?q=%s' % query
    return params


def response(resp):
    results = loads(resp.text)

    return results
