"""
 Google (Images)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   yes
 @results     HTML chunk
 @stable      no
 @parse       url, title, img_src
"""

from urllib import urlencode
from urlparse import parse_qs
from json import loads
from lxml import html

# engine dependent config
categories = ['images']
paging = True
safesearch = True

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=isch'\
    '&ijn=1'\
    '&start={offset}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 100

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      safesearch=safesearch)

    if safesearch and params['safesearch']:
        params['url'] += '&' + urlencode({'safe': 'active'})

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@data-ved]'):
        data_url = result.xpath('./a/@href')[0]
        data_query = {k: v[0] for k, v in parse_qs(data_url.split('?', 1)[1]).iteritems()}

        metadata = loads(result.xpath('./div[@class="rg_meta"]/text()')[0])

        thumbnail_src = metadata['tu']

        # http to https
        thumbnail_src = thumbnail_src.replace("http://", "https://")

        # append result
        results.append({'url': data_query['imgrefurl'],
                        'title': metadata['pt'],
                        'content': metadata['s'],
                        'thumbnail_src': metadata['tu'],
                        'img_src': data_query['imgurl'],
                        'template': 'images.html'})

    # return results
    print len(results)
    return results
