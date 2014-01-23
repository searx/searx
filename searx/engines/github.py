from urllib import urlencode
from json import loads
from cgi import escape

categories = ['it']

search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&{query}'  # noqa

accept_header = 'application/vnd.github.preview.text-match+json'


def request(query, params):
    global search_url
    params['url'] = search_url.format(query=urlencode({'q': query}))
    params['headers']['Accept'] = accept_header
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)
    if not 'items' in search_res:
        return results
    for res in search_res['items']:
        title = res['name']
        url = res['html_url']
        if res['description']:
            content = escape(res['description'][:500])
        else:
            content = ''
        results.append({'url': url, 'title': title, 'content': content})
    return results
