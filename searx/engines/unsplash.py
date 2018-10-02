"""
 Unsplash

 @website     https://unsplash.com
 @provide-api yes (https://unsplash.com/developers)

 @using-api   no
 @results     JSON (using search portal's infiniscroll API)
 @stable      no (JSON format could change any time)
 @parse       url, title, img_src, thumbnail_src
"""

from searx.url_utils import urlencode
from json import loads

url = 'https://unsplash.com/'
search_url = url + 'napi/search/photos?'
categories = ['images']
page_size = 20
paging = True


def request(query, params):
    params['url'] = search_url + urlencode({'query': query, 'page': params['pageno'], 'per_page': page_size})
    return params


def response(resp):
    results = []
    json_data = loads(resp.text)

    for result in json_data['results']:
        results.append({'template': 'images.html',
                        'url': result['links']['html'],
                        'thumbnail_src': result['urls']['thumb'],
                        'img_src': result['urls']['full'],
                        'title': result['description'],
                        'content': ''})
    return results
