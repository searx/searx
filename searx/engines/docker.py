from urllib import urlencode
from json import loads
from cgi import escape

categories = ['docker']

search_url = 'https://index.docker.io/v1/search?{query}'

accept_header = 'application/json'


def request(query, params):
    global search_url
    params['url'] = search_url.format(query=urlencode({'q': query}))
    params['headers']['Accept'] = accept_header
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)
    if not 'results' in search_res:
        return false
    for res in search_res['results']:
        title = res['name']

        base = 'https://index.docker.io/'
        if not '/' in title:
            url = base + '_/' + title
        else:
            url = base + 'u/' + title

        if res['description']:
            content = escape(res['description'][:500])
        else:
            content = ''
        results.append({'url': url, 'title': title, 'content': content})
    return results
