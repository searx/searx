"""
 Deezer (Music)

 @website     https://deezer.com
 @provide-api yes (http://developers.deezer.com/api/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content, embedded
"""

from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['music']
paging = True

# search-url
url = 'https://api.deezer.com/'
search_url = url + 'search?{query}&index={offset}'

embedded_url = '<iframe scrolling="no" frameborder="0" allowTransparency="true" ' +\
    'data-src="https://www.deezer.com/plugins/player?type=tracks&id={audioid}" ' +\
    'width="540" height="80"></iframe>'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 25

    params['url'] = search_url.format(query=urlencode({'q': query}), offset=offset)

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

            if url.startswith('http://'):
                url = 'https' + url[4:]

            content = u'{} - {} - {}'.format(
                result['artist']['name'],
                result['album']['title'],
                result['title'])

            embedded = embedded_url.format(audioid=result['id'])

            # append result
            results.append({'url': url,
                            'title': title,
                            'embedded': embedded,
                            'content': content})

    # return results
    return results
