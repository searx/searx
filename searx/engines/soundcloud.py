from json import loads
from urllib import urlencode

categories = ['music']

guest_client_id = 'b45b1aa10f1ac2941910a7f0d10f8e28'
url = 'https://api.soundcloud.com/'
search_url = url + 'search?{query}&facet=model&limit=20&offset=0&linked_partitioning=1&client_id='+guest_client_id  # noqa


def request(query, params):
    global search_url
    params['url'] = search_url.format(query=urlencode({'q': query}))
    return params


def response(resp):
    global base_url
    results = []
    search_res = loads(resp.text)
    for result in search_res.get('collection', []):
        if result['kind'] in ('track', 'playlist'):
            title = result['title']
            content = result['description']
            results.append({'url': result['permalink_url'],
                            'title': title,
                            'content': content})
    return results
