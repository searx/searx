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
        if len(result['media$group']['media$thumbnail']):
            content += '<img src="%s" />' % (result['media$group']['media$thumbnail'][0]['url'])
        if len(content):
            content += '<br />' + result['content']['$t']
        else:
            content = result['content']['$t']

        results.append({'url': url, 'title': title, 'content': content})

    return results

