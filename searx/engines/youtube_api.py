# Youtube (Videos)
#
# @website     https://www.youtube.com/
# @provide-api yes (https://developers.google.com/apis-explorer/#p/youtube/v3/youtube.search.list)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, publishedDate, thumbnail, embedded

from json import loads
from dateutil import parser
from searx.url_utils import urlencode

# engine dependent config
categories = ['videos', 'music']
paging = False
language_support = True
api_key = None

# search-url
base_url = 'https://www.googleapis.com/youtube/v3/search'
search_url = base_url + '?part=snippet&{query}&maxResults=20&key={api_key}'

embedded_url = '<iframe width="540" height="304" ' +\
    'data-src="//www.youtube-nocookie.com/embed/{videoid}" ' +\
    'frameborder="0" allowfullscreen></iframe>'

base_youtube_url = 'https://www.youtube.com/watch?v='


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      api_key=api_key)

    # add language tag if specified
    if params['language'] != 'all':
        params['url'] += '&relevanceLanguage=' + params['language'].split('-')[0]

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # return empty array if there are no results
    if 'items' not in search_results:
        return []

    # parse results
    for result in search_results['items']:
        videoid = result['id']['videoId']

        title = result['snippet']['title']
        content = ''
        thumbnail = ''

        pubdate = result['snippet']['publishedAt']
        publishedDate = parser.parse(pubdate)

        thumbnail = result['snippet']['thumbnails']['high']['url']

        content = result['snippet']['description']

        url = base_youtube_url + videoid

        embedded = embedded_url.format(videoid=videoid)

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'embedded': embedded,
                        'thumbnail': thumbnail})

    # return results
    return results
