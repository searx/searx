from lxml import html
from urllib import urlencode
from urlparse import urlparse, urljoin
from cgi import escape
from lxml.etree import _ElementStringResult

search_url    = None
results_xpath = None
url_xpath     = None
content_xpath = None
title_xpath   = None

def extract_url(xpath_results):
    url = ''
    parsed_search_url = urlparse(search_url)
    if type(xpath_results) == list:
        if not len(xpath_results):
            raise Exception('Empty url resultset')
        if type(xpath_results[0]) == _ElementStringResult:
            url = ''.join(xpath_results)
            if url.startswith('//'):
                url = parsed_search_url.scheme+url
            elif url.startswith('/'):
                url = urljoin(search_url, url)
        #TODO
        else:
            url = xpath_results[0].attrib.get('href')
    else:
        raise Exception('Cannot handle xpath url resultset')
    if not url.startswith('http://') or not url.startswith('https://'):
        url = 'http://'+url
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise Exception('Cannot parse url')
    return url

def request(query, params):
    query = urlencode({'q': query})[2:]
    params['url'] = search_url.format(query=query)
    params['query'] = query
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    query = resp.search_params['query']
    for result in dom.xpath(results_xpath):
        url = extract_url(result.xpath(url_xpath))
        title = ' '.join(result.xpath(title_xpath))
        content = escape(' '.join(result.xpath(content_xpath))).replace(query, '<b>{0}</b>'.format(query))
        results.append({'url': url, 'title': title, 'content': content})

    return results
