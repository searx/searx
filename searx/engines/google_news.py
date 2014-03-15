#!/usr/bin/env python

from urllib import urlencode
from json import loads
from datetime import datetime, timedelta

categories = ['news']

url = 'https://ajax.googleapis.com/'
search_url = url + 'ajax/services/search/news?v=2.0&start={offset}&rsz=large&safe=off&filter=off&{query}&hl={language}'  # noqa

paging = True
language_support = True


def request(query, params):
    offset = (params['pageno'] - 1) * 8
    language = 'en-US'
    if params['language'] != 'all':
        language = params['language'].replace('_', '-')
    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}),
                                      language=language)
    return params


def response(resp):
    results = []
    search_res = loads(resp.text)

    if not search_res.get('responseData', {}).get('results'):
        return []

    for result in search_res['responseData']['results']:
# S.149 (159), library.pdf
# datetime.strptime("Mon, 10 Mar 2014 16:26:15 -0700", "%a, %d %b %Y %H:%M:%S %z")
#        publishedDate = parse(result['publishedDate'])
        publishedDate = datetime.strptime(str.join(' ',result['publishedDate'].split(None)[0:5]), "%a, %d %b %Y %H:%M:%S")
        #utc_offset = timedelta(result['publishedDate'].split(None)[5])  # local = utc + offset
        #publishedDate = publishedDate + utc_offset

        results.append({'url': result['unescapedUrl'],
                        'title': result['titleNoFormatting'],
						'publishedDate': publishedDate,
                        'content': result['content']})
    return results
