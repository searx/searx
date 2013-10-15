import json

def request(query, params):
    params['url'] = 'http://api.duckduckgo.com/?q=%s&format=json&pretty=0' % query
    return params


def response(resp):
    search_res = json.loads(resp.text)
    results = []
    if 'Definition' in search_res:
        if search_res.get('AbstractURL'):
            res = {'title'   : search_res.get('Heading', '')
                  ,'content' : search_res.get('Definition', '')
                  ,'url'     : search_res.get('AbstractURL', '')
                  }
            results.append(res)

    return results
