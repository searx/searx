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
from searx.url_utils import urlencode
from datetime import datetime

# engine dependent config
categories = ['news', 'social media']
paging = True

# search-url
base_url = 'https://digg.com/'
search_url = base_url + 'api/search/?{query}&from={position}&size=20&format=html'

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
    offset = (params['pageno'] - 1) * 20
    params['url'] = search_url.format(position=offset,
                                      query=urlencode({'q': query}))
    params['cookies']['frontend.auid'] = ''.join(random.choice(
        digg_cookie_chars) for _ in range(22))
    return params


# get response from search-request
def response(resp):
    results = []

    search_result = loads(resp.text)

    # parse results
    for result in search_result['mapped']:

        published = datetime.strptime(result['created']['ISO'], "%Y-%m-%d %H:%M:%S")
        # append result
        results.append({'url': result['url'],
                        'title': result['title'],
                        'content': result['excerpt'],
                        'template': 'videos.html',
                        'publishedDate': published,
                        'thumbnail': result['images']['thumbImage']})

    # return results
    return results
