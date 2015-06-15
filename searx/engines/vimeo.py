#  Vimeo (Videos)
#
# @website     https://vimeo.com/
# @provide-api yes (http://developer.vimeo.com/api),
#              they have a maximum count of queries/hour
#
# @using-api   no (TODO, rewrite to api)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, publishedDate,  thumbnail, embedded
#
# @todo        rewrite to api
# @todo        set content-parameter with correct data

from urllib import urlencode
from lxml import html
from HTMLParser import HTMLParser
from searx.engines.xpath import extract_text
from dateutil import parser

# engine dependent config
categories = ['videos']
paging = True

# search-url
base_url = 'https://vimeo.com'
search_url = base_url + '/search/page:{pageno}?{query}'

# specific xpath variables
results_xpath = '//div[contains(@class,"results_grid")]/ul/li'
url_xpath = './/a/@href'
title_xpath = './/span[@class="title"]'
thumbnail_xpath = './/img[@class="js-clip_thumbnail_image"]/@src'
publishedDate_xpath = './/time/attribute::datetime'

embedded_url = '<iframe data-src="//player.vimeo.com/video{videoid}" ' +\
    'width="540" height="304" frameborder="0" ' +\
    'webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)
    p = HTMLParser()

    # parse results
    for result in dom.xpath(results_xpath):
        videoid = result.xpath(url_xpath)[0]
        url = base_url + videoid
        title = p.unescape(extract_text(result.xpath(title_xpath)))
        thumbnail = extract_text(result.xpath(thumbnail_xpath)[0])
        publishedDate = parser.parse(extract_text(result.xpath(publishedDate_xpath)[0]))
        embedded = embedded_url.format(videoid=videoid)

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': '',
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'embedded': embedded,
                        'thumbnail': thumbnail})

    # return results
    return results
