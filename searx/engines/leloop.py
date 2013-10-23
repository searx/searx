from urllib import urlencode
from lxml import html
from urlparse import urljoin
from cgi import escape

categories = ['it']

base_url = 'http://wiki.leloop.org/'
search_url = base_url+'index.php?title=Special:Search&'

def request(query, params):
    global search_url
    params['url'] = search_url + urlencode({'search': query})
    return params

def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//ul[@class="mw-search-results"]/li'):
        link = result.xpath('.//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = link.attrib.get('title')
        content = escape(' '.join(result.xpath('.//div[@class="searchresult"]//text()'))).encode('ascii', 'xmlcharrefreplace')
        results.append({'url': url, 'title': title, 'content': content})

    return results
