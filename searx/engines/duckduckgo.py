from urllib import urlencode
from lxml.html import fromstring
from searx.utils import html_to_text

url = 'https://duckduckgo.com/html?{query}&s={offset}'
locale = 'us-en'


def request(query, params):
    offset = (params['pageno'] - 1) * 30
    q = urlencode({'q': query,
                   'l': locale})
    params['url'] = url.format(query=q, offset=offset)
    return params


def response(resp):
    result_xpath = '//div[@class="results_links results_links_deep web-result"]'  # noqa
    url_xpath = './/a[@class="large"]/@href'
    title_xpath = './/a[@class="large"]//text()'
    content_xpath = './/div[@class="snippet"]//text()'
    results = []

    doc = fromstring(resp.text)

    for r in doc.xpath(result_xpath):
        try:
            res_url = r.xpath(url_xpath)[-1]
        except:
            continue
        if not res_url:
            continue
        title = html_to_text(''.join(r.xpath(title_xpath)))
        content = html_to_text(''.join(r.xpath(content_xpath)))
        results.append({'title': title,
                        'content': content,
                        'url': res_url})

    return results


#from json import loads
#search_url = url + 'd.js?{query}&p=1&s={offset}'
#
#paging = True
#
#
#def request(query, params):
#    offset = (params['pageno'] - 1) * 30
#    q = urlencode({'q': query,
#                   'l': locale})
#    params['url'] = search_url.format(query=q, offset=offset)
#    return params
#
#
#def response(resp):
#    results = []
#    search_res = loads(resp.text[resp.text.find('[{'):-2])[:-1]
#    for r in search_res:
#        if not r.get('t'):
#            continue
#        results.append({'title': r['t'],
#                       'content': html_to_text(r['a']),
#                       'url': r['u']})
#    return results
