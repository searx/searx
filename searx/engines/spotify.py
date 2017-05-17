"""
 Spotify (Music)

 @website     https://spotify.com
 @provide-api yes (https://developer.spotify.com/web-api/search-item/)

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
url = 'https://api.spotify.com/'
search_url = url + 'v1/search?{query}&type=track&offset={offset}'

embedded_url = '<iframe data-src="https://embed.spotify.com/?uri=spotify:track:{audioid}"\
     width="300" height="80" frameborder="0" allowtransparency="true"></iframe>'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 20

    params['url'] = search_url.format(query=urlencode({'q': query}), offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # parse results
    for result in search_res.get('tracks', {}).get('items', {}):
        if result['type'] == 'track':
            title = result['name']
            url = result['external_urls']['spotify']
            content = u'{} - {} - {}'.format(
                result['artists'][0]['name'],
                result['album']['name'],
                result['name'])

            embedded = embedded_url.format(audioid=result['id'])

            # append result
            results.append({'url': url,
                            'title': title,
                            'embedded': embedded,
                            'content': content})

    # return results
    return results
