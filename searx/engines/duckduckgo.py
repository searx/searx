"""
 DuckDuckGo (Web)

 @website     https://duckduckgo.com/
 @provide-api yes (https://duckduckgo.com/api),
              but not all results from search-site

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        rewrite to api
 @todo        language support
              (the current used site does not support language-change)
"""

from urllib import urlencode
from lxml.html import fromstring
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['general']
paging = True
language_support = True

# search-url
url = 'https://duckduckgo.com/html?{query}&s={offset}'

# specific xpath variables
result_xpath = '//div[@class="results_links results_links_deep web-result"]'  # noqa
url_xpath = './/a[@class="large"]/@href'
title_xpath = './/a[@class="large"]'
content_xpath = './/div[@class="snippet"]'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 30

    if params['language'] == 'all':
        locale = 'en-us'
    else:
        locale = params['language'].replace('_', '-').lower()

    params['url'] = url.format(
        query=urlencode({'q': query, 'kl': locale}),
        offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    doc = fromstring(resp.text)

    # parse results
    for r in doc.xpath(result_xpath):
        try:
            res_url = r.xpath(url_xpath)[-1]
        except:
            continue

        if not res_url:
            continue

        title = extract_text(r.xpath(title_xpath))
        content = extract_text(r.xpath(content_xpath))

        # append result
        results.append({'title': title,
                        'content': content,
                        'url': res_url})

    # return results
    return results
