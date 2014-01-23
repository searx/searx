from urllib import urlencode
from lxml import html

base_url = 'https://startpage.com/'
search_url = base_url+'do/search'


def request(query, params):
    global search_url
    query = urlencode({'q': query})[2:]
    params['url'] = search_url
    params['method'] = 'POST'
    params['data'] = {'query': query}
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.content)
    # ads xpath //div[@id="results"]/div[@id="sponsored"]//div[@class="result"]
    # not ads: div[@class="result"] are the direct childs of div[@id="results"]
    for result in dom.xpath('//div[@id="results"]/div[@class="result"]'):
        link = result.xpath('.//h3/a')[0]
        url = link.attrib.get('href')
        title = link.text_content()
        content = result.xpath('./p[@class="desc"]')[0].text_content()
        results.append({'url': url, 'title': title, 'content': content})
    return results
