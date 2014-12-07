## Youtube (Videos)
#
# @website     https://www.youtube.com/
# @provide-api yes (http://gdata-samples-youtube-search-py.appspot.com/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content, publishedDate, thumbnail

from json import loads
from urllib import urlencode
from dateutil import parser

# engine dependent config
categories = ['videos', 'music']
paging = True
language_support = True

# search-url
base_url = 'https://gdata.youtube.com/feeds/api/videos'
search_url = base_url + '?alt=json&{query}&start-index={index}&max-results=5'  # noqa


# do search-request
def request(query, params):
    index = (params['pageno'] - 1) * 5 + 1

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      index=index)

    # add language tag if specified
    if params['language'] != 'all':
        params['url'] += '&lr=' + params['language'].split('_')[0]

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # return empty array if there are no results
    if not 'feed' in search_results:
        return []

    feed = search_results['feed']

    # parse results
    for result in feed['entry']:
        url = [x['href'] for x in result['link'] if x['type'] == 'text/html']

        if not url:
            return

        # remove tracking
        url = url[0].replace('feature=youtube_gdata', '')
        if url.endswith('&'):
            url = url[:-1]

        title = result['title']['$t']
        content = ''
        thumbnail = ''

        pubdate = result['published']['$t']
        publishedDate = parser.parse(pubdate)

        if result['media$group']['media$thumbnail']:
            thumbnail = result['media$group']['media$thumbnail'][0]['url']

        content = result['content']['$t']

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    # return results
    return results
