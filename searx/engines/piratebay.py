from lxml import html
from urlparse import urljoin
from cgi import escape
from urllib import quote

categories = ['videos', 'music']

url = 'https://thepiratebay.se/'
search_url = url + 'search/{search_term}/0/99/{search_type}'
search_types = {'videos': '200'
               ,'music' : '100'
               }

def request(query, params):
    params['url'] = search_url.format(search_term=quote(query), search_type=search_types.get(params['category']))
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    search_res = dom.xpath('//table[@id="searchResult"]//tr')
    if not search_res:
        return results
    for result in search_res[1:]:
        link = result.xpath('.//div[@class="detName"]//a')[0]
        href = urljoin(url, link.attrib.get('href'))
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//font[@class="detDesc"]//text()')))
        seed, leech = result.xpath('.//td[@align="right"]/text()')[:2]
        content += '<br />Seed: %s, Leech: %s' % (seed, leech)
        magnetlink = result.xpath('.//a[@title="Download this torrent using magnet"]')[0]
        content += '<br /><a href="%s">magnet link</a>' % urljoin(url, magnetlink.attrib['href'])
        results.append({'url': href, 'title': title, 'content': content})
    return results
