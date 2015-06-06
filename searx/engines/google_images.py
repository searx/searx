"""
 Google (Images)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/web-search/docs/),
              deprecated!

 @using-api   yes
 @results     JSON
 @stable      yes (but deprecated)
 @parse       url, title, img_src
"""

from urllib import urlencode, unquote
from json import loads

# engine dependent config
categories = ['images']
paging = True
safesearch = True

# search-url
url = 'https://ajax.googleapis.com/'
search_url = url + 'ajax/services/search/images?v=1.0&start={offset}&rsz=large&safe={safesearch}&filter=off&{query}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 8

    if params['safesearch'] == 0:
        safesearch = 'off'
    else:
        safesearch = 'on'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      safesearch=safesearch)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # return empty array if there are no results
    if not search_res.get('responseData', {}).get('results'):
        return []

    # parse results
    for result in search_res['responseData']['results']:
        href = result['originalContextUrl']
        title = result['title']
        if 'url' not in result:
            continue
        thumbnail_src = result['tbUrl']

        # http to https
        thumbnail_src = thumbnail_src.replace("http://", "https://")

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': result['content'],
                        'thumbnail_src': thumbnail_src,
                        'img_src': unquote(result['url']),
                        'template': 'images.html'})

    # return results
    return results
