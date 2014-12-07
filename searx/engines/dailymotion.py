## Dailymotion (Videos)
#
# @website     https://www.dailymotion.com
# @provide-api yes (http://www.dailymotion.com/developer)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, thumbnail
#
# @todo        set content-parameter with correct data

from urllib import urlencode
from json import loads

# engine dependent config
categories = ['videos']
paging = True
language_support = True

# search-url
# see http://www.dailymotion.com/doc/api/obj-video.html
search_url = 'https://api.dailymotion.com/videos?fields=title,description,duration,url,thumbnail_360_url&sort=relevance&limit=5&page={pageno}&{query}'  # noqa


# do search-request
def request(query, params):
    if params['language'] == 'all':
        locale = 'en-US'
    else:
        locale = params['language']

    params['url'] = search_url.format(
        query=urlencode({'search': query, 'localization': locale}),
        pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # return empty array if there are no results
    if not 'list' in search_res:
        return []

    # parse results
    for res in search_res['list']:
        title = res['title']
        url = res['url']
        #content = res['description']
        content = ''
        thumbnail = res['thumbnail_360_url']

        results.append({'template': 'videos.html',
                        'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': thumbnail})

    # return results
    return results
