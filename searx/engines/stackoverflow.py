from urlparse import urljoin
from cgi import escape
from urllib import urlencode
from lxml import html

categories = ['it']

url = 'http://stackoverflow.com/'
search_url = url+'search?{query}&page={pageno}'
result_xpath = './/div[@class="excerpt"]//text()'

paging = True


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      pageno=params['pageno'])
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//div[@class="question-summary search-result"]'):
        link = result.xpath('.//div[@class="result-link"]//a')[0]
        href = urljoin(url, link.attrib.get('href'))
        title = escape(' '.join(link.xpath('.//text()')))
        content = escape(' '.join(result.xpath(result_xpath)))
        results.append({'url': href, 'title': title, 'content': content})
    return results
