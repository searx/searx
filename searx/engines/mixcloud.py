## Mixcloud (Music)
#
# @website     https://http://www.mixcloud.com/
# @provide-api yes (http://www.mixcloud.com/developers/
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, embedded, publishedDate

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from json import loads
from urllib.parse import urlencode
from dateutil import parser

# engine dependent config
categories = ['music']
paging = True

# search-url
url = 'http://api.mixcloud.com/'
search_url = url + 'search/?{query}&type=cloudcast&limit=10&offset={offset}'

embedded_url = '<iframe scrolling="no" frameborder="0" allowTransparency="true" ' +\
    'data-src="https://www.mixcloud.com/widget/iframe/?feed={url}" width="300" height="300"></iframe>'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # parse results
    for result in search_res.get('data', []):
        title = result['name']
        url = result['url']
        content = result['user']['name']
        embedded = embedded_url.format(url=url)
        publishedDate = parser.parse(result['created_time'])

        # append result
        results.append({'url': url,
                        'title': title,
                        'embedded': embedded,
                        'publishedDate': publishedDate,
                        'content': content})

    # return results
    return results
