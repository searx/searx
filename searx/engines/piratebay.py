from lxml import html
from urlparse import urljoin
from cgi import escape
from urllib import quote

categories = ['videos', 'music']

url = 'https://thepiratebay.se/'
search_url = url + 'search/{search_term}/0/99/{search_type}'
search_types = {'videos': '200',
                'music': '100',
                'files': '0'}

magnet_xpath = './/a[@title="Download this torrent using magnet"]'
content_xpath = './/font[@class="detDesc"]//text()'


def request(query, params):
    search_type = search_types.get(params['category'])
    params['url'] = search_url.format(search_term=quote(query),
                                      search_type=search_type)
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
        content = escape(' '.join(result.xpath(content_xpath)))
        seed, leech = result.xpath('.//td[@align="right"]/text()')[:2]
        magnetlink = result.xpath(magnet_xpath)[0]
        results.append({'url': href,
                        'title': title,
                        'content': content,
                        'seed': seed,
                        'leech': leech,
                        'magnetlink': magnetlink.attrib['href'],
                        'template': 'torrent.html'})
    return results
