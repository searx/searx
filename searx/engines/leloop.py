from urllib import urlencode
from lxml import html
from urlparse import urljoin

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
    for result in dom.xpath('//div[contains(@class, "mw-search-result-heading")]'):
        link = result.xpath('.//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = link.attrib.get('title')
        content = result.find_text('.//div[contains(@class, "searchresult")]')[0]
        results.append({'url': url, 'title': title, 'content': content})

    return results
