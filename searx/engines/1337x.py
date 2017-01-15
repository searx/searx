from urllib import quote
from lxml import html
from searx.engines.xpath import extract_text
from urlparse import urljoin

url = 'https://1337x.to/'
search_url = url + 'search/{search_term}/{pageno}/'
categories = ['videos', 'music', 'files']
paging = True

def request(query, params):
    params['url'] = search_url.format(search_term=quote(query), pageno=params['pageno'])

    return params

def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath('//table[contains(@class, "table-list")]/tbody//tr'):
        href = urljoin(url, result.xpath('./td[contains(@class, "name")]/a[2]/@href')[0])
        title = extract_text(result.xpath('./td[contains(@class, "name")]/a[2]'))

        results.append({'url': href,
                        'title': title,
                        'content': ''})

    return results
