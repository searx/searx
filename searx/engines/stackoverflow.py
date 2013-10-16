from urllib import quote
from lxml import html
from urlparse import urljoin

base_url = 'http://stackoverflow.com/'
search_url = base_url+'search?q='

def request(query, params):
    global search_url
    query = quote(query.replace(' ', '+'), safe='+')
    params['url'] = search_url + query
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//div[@class="question-summary search-result"]'):
        link = result.xpath('.//div[@class="result-link"]//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = ' '.join(link.xpath('.//text()'))
        content = ' '.join(result.xpath('.//div[@class="excerpt"]//text()'))
        results.append({'url': url, 'title': title, 'content': content})
    return results
