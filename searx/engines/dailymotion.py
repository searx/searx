"""
 Dailymotion (Videos)

 @website     https://www.dailymotion.com
 @provide-api yes (http://www.dailymotion.com/developer)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, thumbnail, publishedDate, embedded

 @todo        set content-parameter with correct data
"""

from json import loads
from datetime import datetime
from searx.url_utils import urlencode

# engine dependent config
categories = ['videos']
paging = True
language_support = True

# search-url
# see http://www.dailymotion.com/doc/api/obj-video.html
search_url = 'https://api.dailymotion.com/videos?fields=created_time,title,description,duration,url,thumbnail_360_url,id&sort=relevance&limit=5&page={pageno}&{query}'  # noqa
embedded_url = '<iframe frameborder="0" width="540" height="304" ' +\
    'data-src="//www.dailymotion.com/embed/video/{videoid}" allowfullscreen></iframe>'

supported_languages_url = 'https://api.dailymotion.com/languages'


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
    if 'list' not in search_res:
        return []

    # parse results
    for res in search_res['list']:
        title = res['title']
        url = res['url']
        content = res['description']
        thumbnail = res['thumbnail_360_url']
        publishedDate = datetime.fromtimestamp(res['created_time'], None)
        embedded = embedded_url.format(videoid=res['id'])

        # http to https
        thumbnail = thumbnail.replace("http://", "https://")

        results.append({'template': 'videos.html',
                        'url': url,
                        'title': title,
                        'content': content,
                        'publishedDate': publishedDate,
                        'embedded': embedded,
                        'thumbnail': thumbnail})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = {}

    response_json = loads(resp.text)

    for language in response_json['list']:
        supported_languages[language['code']] = {}

        name = language['native_name']
        if name:
            supported_languages[language['code']]['name'] = name
        english_name = language['name']
        if english_name:
            supported_languages[language['code']]['english_name'] = english_name

    return supported_languages
