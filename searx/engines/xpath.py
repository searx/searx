from lxml import html
from urllib import urlencode, unquote
from urlparse import urlparse, urljoin
from lxml.etree import _ElementStringResult, _ElementUnicodeResult
from searx.utils import html_to_text

search_url = None
url_xpath = None
content_xpath = None
title_xpath = None
suggestion_xpath = ''
results_xpath = ''


'''
if xpath_results is list, extract the text from each result and concat the list
if xpath_results is a xml element, extract all the text node from it
   ( text_content() method from lxml )
if xpath_results is a string element, then it's already done
'''


def extract_text(xpath_results):
    if type(xpath_results) == list:
        # it's list of result : concat everything using recursive call
        if not xpath_results:
            raise Exception('Empty url resultset')
        result = ''
        for e in xpath_results:
            result = result + extract_text(e)
        return result
    elif type(xpath_results) in [_ElementStringResult, _ElementUnicodeResult]:
        # it's a string
        return ''.join(xpath_results)
    else:
        # it's a element
        return html_to_text(xpath_results.text_content())


def extract_url(xpath_results, search_url):
    url = extract_text(xpath_results)

    if url.startswith('//'):
        # add http or https to this kind of url //example.com/
        parsed_search_url = urlparse(search_url)
        url = parsed_search_url.scheme+url
    elif url.startswith('/'):
        # fix relative url to the search engine
        url = urljoin(search_url, url)

    # normalize url
    url = normalize_url(url)

    return url


def normalize_url(url):
    parsed_url = urlparse(url)

    # add a / at this end of the url if there is no path
    if not parsed_url.netloc:
        raise Exception('Cannot parse url')
    if not parsed_url.path:
        url += '/'

    # FIXME : hack for yahoo
    if parsed_url.hostname == 'search.yahoo.com'\
       and parsed_url.path.startswith('/r'):
        p = parsed_url.path
        mark = p.find('/**')
        if mark != -1:
            return unquote(p[mark+3:]).decode('utf-8')

    return url


def request(query, params):
    query = urlencode({'q': query})[2:]
    params['url'] = search_url.format(query=query)
    params['query'] = query
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    if results_xpath:
        for result in dom.xpath(results_xpath):
            url = extract_url(result.xpath(url_xpath), search_url)
            title = extract_text(result.xpath(title_xpath)[0])
            content = extract_text(result.xpath(content_xpath)[0])
            results.append({'url': url, 'title': title, 'content': content})
    else:
        for url, title, content in zip(
            (extract_url(x, search_url) for
             x in dom.xpath(url_xpath)),
            map(extract_text, dom.xpath(title_xpath)),
            map(extract_text, dom.xpath(content_xpath))
        ):
            results.append({'url': url, 'title': title, 'content': content})

    if not suggestion_xpath:
        return results
    for suggestion in dom.xpath(suggestion_xpath):
        results.append({'suggestion': extract_text(suggestion)})
    return results
