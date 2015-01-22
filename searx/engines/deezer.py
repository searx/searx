## Deezer (Music)
#
# @website     https://deezer.com
# @provide-api yes (http://developers.deezer.com/api/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, embedded

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from json import loads
from urllib.parse import urlencode

# engine dependent config
categories = ['music']
paging = True

# search-url
url = 'http://api.deezer.com/'
search_url = url + 'search?{query}&index={offset}'

embedded_url = '<iframe scrolling="no" frameborder="0" allowTransparency="true" ' +\
    'data-src="http://www.deezer.com/plugins/player?type=tracks&id={audioid}" ' +\
    'width="540" height="80"></iframe>'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 25

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # parse results
    for result in search_res.get('data', []):
        if result['type'] == 'track':
            title = result['title']
            url = result['link']
            content = result['artist']['name'] +\
                " &bull; " +\
                result['album']['title'] +\
                " &bull; " + result['title']
            embedded = embedded_url.format(audioid=result['id'])

            # append result
            results.append({'url': url,
                            'title': title,
                            'embedded': embedded,
                            'content': content})

    # return results
    return results
