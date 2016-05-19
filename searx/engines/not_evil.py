"""
 not Evil (Onions)

 @website     http://hss3uro2hsxfogfq.onion
 @provide-api yes (http://hss3uro2hsxfogfq.onion/api.htm)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content
"""

from urllib.parse import urlencode
from lxml import html
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['onions']
paging = True
page_size = 20

# search-url
base_url = 'http://hss3uro2hsxfogfq.onion/'
search_url = 'index.php?{query}&hostLimit=20&start={pageno}&numRows={page_size}'

# specific xpath variables
results_xpath = '//*[@id="content"]/div/p'
url_xpath = './span[1]'
title_xpath = './a[1]'
content_xpath = './text()'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * page_size

    params['url'] = base_url + search_url.format(pageno=offset,
                                                 query=urlencode({'q': query}),
                                                 page_size=page_size)

    return params


# get response from search-request
def response(resp):
    results = []

    # needed because otherwise requests guesses wrong encoding
    resp.encoding = 'utf8'
    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        url = extract_text(result.xpath(url_xpath)[0])
        title = extract_text(result.xpath(title_xpath)[0])
        content = extract_text(result.xpath(content_xpath))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'is_onion': True})

    return results
