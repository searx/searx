"""
Frinkiac (Images)

@website     https://www.frinkiac.com
@provide-api no
@using-api   no
@results     JSON
@stable      no
@parse       url, title, img_src
"""

from json import loads
from searx.url_utils import urlencode

categories = ['images']

BASE = 'https://frinkiac.com/'
SEARCH_URL = '{base}api/search?{query}'
RESULT_URL = '{base}?{query}'
THUMB_URL = '{base}img/{episode}/{timestamp}/medium.jpg'
IMAGE_URL = '{base}img/{episode}/{timestamp}.jpg'


def request(query, params):
    params['url'] = SEARCH_URL.format(base=BASE, query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    response_data = loads(resp.text)
    for result in response_data:
        episode = result['Episode']
        timestamp = result['Timestamp']

        results.append({'template': 'images.html',
                        'url': RESULT_URL.format(base=BASE,
                                                 query=urlencode({'p': 'caption', 'e': episode, 't': timestamp})),
                        'title': episode,
                        'content': '',
                        'thumbnail_src': THUMB_URL.format(base=BASE, episode=episode, timestamp=timestamp),
                        'img_src': IMAGE_URL.format(base=BASE, episode=episode, timestamp=timestamp)})

    return results
