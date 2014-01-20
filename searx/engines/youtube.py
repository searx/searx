from json import loads
from urllib import urlencode

categories = ['videos']

search_url = 'https://gdata.youtube.com/feeds/api/videos?alt=json&{query}'


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    search_results = loads(resp.text)
    if not 'feed' in search_results:
        return results
    feed = search_results['feed']
    for result in feed['entry']:
        url = [x['href'] for x in result['link'] if x['type'] == 'text/html']
        if not len(url):
            return
        # remove tracking
        url = url[0].replace('feature=youtube_gdata', '')
        if url.endswith('&'):
            url = url[:-1]
        title = result['title']['$t']
        content = ''

        thumbnail = ''
        if len(result['media$group']['media$thumbnail']):
            thumbnail = result['media$group']['media$thumbnail'][0]['url']
            content += '<a href="{0}" title="{0}" ><img src="{1}" /></a>'.format(url, thumbnail)  # noqa
        if len(content):
            content += '<br />' + result['content']['$t']
        else:
            content = result['content']['$t']

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'template': 'videos.html',
                        'thumbnail': thumbnail})

    return results
