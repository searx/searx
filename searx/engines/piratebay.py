from lxml import html
from urlparse import urljoin
from cgi import escape
from urllib import quote

categories = ['videos', 'music']

base_url = 'https://thepiratebay.sx/'
search_url = base_url + 'search/{search_term}/0/99/{search_type}'
search_types = {'videos': '200'
               ,'music' : '100'
               }

def request(query, params):
    global search_url, search_types
    # 200 is the video category
    params['url'] = search_url.format(search_term=quote(query), search_type=search_types.get(params['category']))
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    search_res = dom.xpath('//table[@id="searchResult"]//tr')
    if not search_res:
        return results
    for result in search_res[1:]:
        link = result.xpath('.//div[@class="detName"]//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//font[@class="detDesc"]//text()')))
        seed, leech = result.xpath('.//td[@align="right"]/text()')[:2]
        content += '<br />Seed: %s, Leech: %s' % (seed, leech)
        results.append({'url': url, 'title': title, 'content': content})
    return results
