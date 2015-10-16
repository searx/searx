"""
 Gigablast (Web)

 @website     http://gigablast.com
 @provide-api yes (http://gigablast.com/api.html)

 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, content
"""

from urllib import urlencode
from cgi import escape
from lxml import etree
from random import randint
from time import time

# engine dependent config
categories = ['general']
paging = True
number_of_results = 5

# search-url, invalid HTTPS certificate
base_url = 'http://gigablast.com/'
search_string = 'search?{query}&n={number_of_results}&s={offset}&xml=1&qh=0&uxid={uxid}&rand={rand}'

# specific xpath variables
results_xpath = '//response//result'
url_xpath = './/url'
title_xpath = './/title'
content_xpath = './/sum'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * number_of_results

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset,
        number_of_results=number_of_results,
        uxid=randint(10000, 10000000),
        rand=int(time()))

    params['url'] = base_url + search_path

    return params


# get response from search-request
def response(resp):
    results = []

    dom = etree.fromstring(resp.content)

    # parse results
    for result in dom.xpath(results_xpath):
        url = result.xpath(url_xpath)[0].text
        title = result.xpath(title_xpath)[0].text
        content = escape(result.xpath(content_xpath)[0].text)

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
