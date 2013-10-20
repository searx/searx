#!/usr/bin/env python

from urllib import urlencode
from json import loads

categories = ['images']

search_url = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&start=0&rsz=large&safe=off&filter=off&'

def request(query, params):
    global search_url
    params['url'] = search_url + urlencode({'q': query})
    return params

def response(resp):
    global base_url
    results = []
    search_res = loads(resp.text)
    if not search_res.get('responseData'):
        return []
    if not search_res['responseData'].get('results'):
        return []
    for result in search_res['responseData']['results']:
        url = result['originalContextUrl']
        title = result['title']
        content = '<a href="%s"><img src="%s" title="%s" style="max-width: 500px; "/></a>' % (result['url'], result['url'], title)
        if result['content']:
            content += '<br />'+result['content']
        results.append({'url': url, 'title': title, 'content': content})
    return results
