## Digg (News, Social media)
#
# @website     https://digg.com/
# @provide-api no
#
# @using-api   no
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content, publishedDate, thumbnail

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import quote_plus
from json import loads
from lxml import html
from cgi import escape
from dateutil import parser

# engine dependent config
categories = ['news', 'social media']
paging = True

# search-url
base_url = 'https://digg.com/'
search_url = base_url+'api/search/{query}.json?position={position}&format=html'

# specific xpath variables
results_xpath = '//article'
link_xpath = './/small[@class="time"]//a'
title_xpath = './/h2//a//text()'
content_xpath = './/p//text()'
pubdate_xpath = './/time'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10
    params['url'] = search_url.format(position=offset,
                                      query=quote_plus(query))
    return params


# get response from search-request
def response(resp):
    results = []

    search_result = loads(resp.text)

    if search_result['html'] == '':
        return results

    dom = html.fromstring(search_result['html'])

    # parse results
    for result in dom.xpath(results_xpath):
        url = result.attrib.get('data-contenturl')
        thumbnail = result.xpath('.//img')[0].attrib.get('src')
        title = ''.join(result.xpath(title_xpath))
        content = escape(''.join(result.xpath(content_xpath)))
        pubdate = result.xpath(pubdate_xpath)[0].attrib.get('datetime')
        publishedDate = parser.parse(pubdate)

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
