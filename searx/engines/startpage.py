from urllib import quote
from lxml import html
from urlparse import urlparse
from cgi import escape

base_url = 'https://startpage.com/'
search_url = base_url+'do/search'

def request(query, params):
    global search_url
    query = quote(query.replace(' ', '+'), safe='+')
    params['url'] = search_url
    params['method'] = 'POST'
    params['data'] = {'query': query}
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.content)
    for result in dom.xpath('//div[@class="result"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        parsed_url = urlparse(url)
        # TODO better google link detection
        if parsed_url.netloc.find('www.google.com') >= 0:
            continue
        title = ' '.join(link.xpath('.//text()'))
        content = escape(' '.join(result.xpath('.//p[@class="desc"]//text()')))
        results.append({'url': url, 'title': title, 'content': content})
    return results
