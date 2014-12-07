## Vimeo (Videos)
#
# @website     https://vimeo.com/
# @provide-api yes (http://developer.vimeo.com/api),
#              they have a maximum count of queries/hour
#
# @using-api   no (TODO, rewrite to api)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, publishedDate,  thumbnail
#
# @todo        rewrite to api
# @todo        set content-parameter with correct data

from urllib import urlencode
from HTMLParser import HTMLParser
from lxml import html
from searx.engines.xpath import extract_text
from dateutil import parser

# engine dependent config
categories = ['videos']
paging = True

# search-url
base_url = 'https://vimeo.com'
search_url = base_url + '/search/page:{pageno}?{query}'

# specific xpath variables
url_xpath = './a/@href'
content_xpath = './a/img/@src'
title_xpath = './a/div[@class="data"]/p[@class="title"]/text()'
results_xpath = '//div[@id="browse_content"]/ol/li'
publishedDate_xpath = './/p[@class="meta"]//attribute::datetime'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'q': query}))

    # TODO required?
    params['cookies']['__utma'] =\
        '00000000.000#0000000.0000000000.0000000000.0000000000.0'

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    p = HTMLParser()

    # parse results
    for result in dom.xpath(results_xpath):
        url = base_url + result.xpath(url_xpath)[0]
        title = p.unescape(extract_text(result.xpath(title_xpath)))
        thumbnail = extract_text(result.xpath(content_xpath)[0])
        publishedDate = parser.parse(extract_text(
            result.xpath(publishedDate_xpath)[0]))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': '',
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
