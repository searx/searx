from json import loads
from urllib import urlencode
from dateutil import parser

categories = ['videos']

search_url = ('https://gdata.youtube.com/feeds/api/videos'
              '?alt=json&{query}&start-index={index}&max-results=25')  # noqa

paging = True


def request(query, params):
    index = (params['pageno'] - 1) * 25 + 1
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      index=index)
    return params


def response(resp):
    results = []
    search_results = loads(resp.text)
    if not 'feed' in search_results:
        return results
    feed = search_results['feed']

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

#"2013-12-31T15:22:51.000Z"
        pubdate = result['published']['$t']
        publishedDate = parser.parse(pubdate)

        if result['media$group']['media$thumbnail']:
            thumbnail = result['media$group']['media$thumbnail'][0]['url']
            content += '<a href="{0}" title="{0}" ><img src="{1}" /></a>'.format(url, thumbnail)  # noqa

        if content:
            content += '<br />' + result['content']['$t']
        else:
            content = result['content']['$t']

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'publishedDate': publishedDate,
                        'thumbnail': thumbnail})

    return results
