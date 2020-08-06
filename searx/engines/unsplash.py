"""
 Unsplash

 @website     https://unsplash.com
 @provide-api yes (https://unsplash.com/developers)

 @using-api   no
 @results     JSON (using search portal's infiniscroll API)
 @stable      no (JSON format could change any time)
 @parse       url, title, img_src, thumbnail_src
"""

from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
from json import loads

url = 'https://unsplash.com/'
search_url = url + 'napi/search/photos?'
categories = ['images']
page_size = 20
paging = True


def clean_url(url):
    parsed = urlparse(url)
    query = [(k, v) for (k, v) in parse_qsl(parsed.query) if k not in ['ixid', 's']]

    return urlunparse((parsed.scheme,
                       parsed.netloc,
                       parsed.path,
                       parsed.params,
                       urlencode(query),
                       parsed.fragment))


def request(query, params):
    params['url'] = search_url + urlencode({'query': query, 'page': params['pageno'], 'per_page': page_size})
    return params


def response(resp):
    results = []
    json_data = loads(resp.text)

    if 'results' in json_data:
        for result in json_data['results']:
            results.append({'template': 'images.html',
                            'url': clean_url(result['links']['html']),
                            'thumbnail_src': clean_url(result['urls']['thumb']),
                            'img_src': clean_url(result['urls']['raw']),
                            'title': result['description'],
                            'content': ''})
    return results
