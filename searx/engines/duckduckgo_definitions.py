import json
from searx import base_result_template

def request(query, params):
    params['url'] = 'http://api.duckduckgo.com/?q=%s&format=json&pretty=0' % query
    return params


def response(resp):
    search_res = json.loads(resp.text)
    results = []
    if 'Definition' in search_res:
        res = {'title'   : search_res.get('Heading', '')
              ,'content' : search_res.get('Definition', '')
              ,'url'     : search_res.get('AbstractURL', '')
              }
        results.append(base_result_template.format(**res))

    return results

#from lxml import html
#def request(query, params):
#    params['method']    = 'POST'
#    params['url']       = 'https://duckduckgo.com/html'
#    params['data']['q'] = query
#    return params
#
#
#def response(resp):
#    dom = html.fromstring(resp.text)
#    results = dom.xpath('//div[@class="results_links results_links_deep web-result"]')
#    return [html.tostring(x) for x in results]
