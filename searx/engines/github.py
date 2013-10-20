from urllib import urlencode
from json import loads

categories = ['it']

search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&'

def request(query, params):
    global search_url
    params['url'] = search_url + urlencode({'q': query})
    params['headers']['Accept'] = 'application/vnd.github.preview.text-match+json'
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)
    if not 'items' in search_res:
        return results
    for res in search_res['items']:
        title = res['name']
        url = res['html_url']
        content = res['description']
        results.append({'url': url, 'title': title, 'content': content})
    return results
