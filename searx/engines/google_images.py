#!/usr/bin/env python

from urllib import urlencode
from json import loads

categories = ['images']

url = 'https://ajax.googleapis.com/'
search_url = url + 'ajax/services/search/images?v=1.0&start=0&rsz=large&safe=off&filter=off&{query}'  # noqa


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)
    if not search_res.get('responseData'):
        return []
    if not search_res['responseData'].get('results'):
        return []
    for result in search_res['responseData']['results']:
        href = result['originalContextUrl']
        title = result['title']
        if not result['url']:
            continue
        results.append({'url': href,
                        'title': title,
                        'content': '',
                        'img_src': result['url'],
                        'template': 'images.html'})
    return results
