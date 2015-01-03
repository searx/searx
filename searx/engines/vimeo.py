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
from lxml import html
from dateutil import parser
from cgi import escape

# engine dependent config
categories = ['videos']
paging = True

# search-url
base_url = 'http://vimeo.com'
search_url = base_url + '/search/page:{pageno}?{query}'

# specific xpath variables
results_xpath = '//div[@id="browse_content"]/ol/li'
url_xpath = './a/@href'
title_xpath = './a/div[@class="data"]/p[@class="title"]'
content_xpath = './a/img/@src'
publishedDate_xpath = './/p[@class="meta"]//attribute::datetime'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        url = base_url + result.xpath(url_xpath)[0]
        title = escape(html.tostring(result.xpath(title_xpath)[0], method='text', encoding='UTF-8').decode("utf-8"))
        thumbnail = result.xpath(content_xpath)[0]
        publishedDate = parser.parse(result.xpath(publishedDate_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': '',
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
