#!/usr/bin/env python

from urllib import urlencode
from json import loads

categories = ['general']

paging = True

url = 'https://ajax.googleapis.com/'
search_url = url + 'ajax/services/search/web?v=1.0&start={offset}&rsz=large&safe=off&filter=off&{query}'  # noqa


def request(query, params):
    offset = (params['pageno'] - 1) * 8
    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)

    if not search_res.get('responseData', {}).get('results'):
        return []

    for result in search_res['responseData']['results']:
        results.append({'url': result['unescapedUrl'],
                        'title': result['titleNoFormatting'],
                        'content': result['content']})
    return results
