"""
 Digg (News, Social media)

 @website     https://digg.com/
 @provide-api no

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content, publishedDate, thumbnail
"""

import random
import string
from dateutil import parser
from json import loads
from lxml import html
from searx.url_utils import quote_plus

# engine dependent config
categories = ['news', 'social media']
paging = True

# search-url
base_url = 'https://digg.com/'
search_url = base_url + 'api/search/{query}.json?position={position}&format=html'

# specific xpath variables
results_xpath = '//article'
link_xpath = './/small[@class="time"]//a'
title_xpath = './/h2//a//text()'
content_xpath = './/p//text()'
pubdate_xpath = './/time'

digg_cookie_chars = string.ascii_uppercase + string.ascii_lowercase +\
    string.digits + "+_"


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10
    params['url'] = search_url.format(position=offset,
                                      query=quote_plus(query))
    params['cookies']['frontend.auid'] = ''.join(random.choice(
        digg_cookie_chars) for _ in range(22))
    return params


# get response from search-request
def response(resp):
    results = []

    search_result = loads(resp.text)

    if 'html' not in search_result or search_result['html'] == '':
        return results

    dom = html.fromstring(search_result['html'])

    # parse results
    for result in dom.xpath(results_xpath):
        url = result.attrib.get('data-contenturl')
        thumbnail = result.xpath('.//img')[0].attrib.get('src')
        title = ''.join(result.xpath(title_xpath))
        content = ''.join(result.xpath(content_xpath))
        pubdate = result.xpath(pubdate_xpath)[0].attrib.get('datetime')
        publishedDate = parser.parse(pubdate)

        # http to https
        thumbnail = thumbnail.replace("http://static.digg.com", "https://static.digg.com")

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
