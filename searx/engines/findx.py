"""
FindX (General, Images, Videos)

@website     https://www.findx.com
@provide-api no
@using-api   no
@results     HTML
@stable      no
@parse       url, title, content, embedded, img_src, thumbnail_src
"""

from dateutil import parser
from json import loads
import re

from lxml import html

from searx import logger
from searx.engines.xpath import extract_text
from searx.engines.youtube_noapi import base_youtube_url, embedded_url
from searx.url_utils import urlencode


paging = True
results_xpath = '//script[@id="initial-state"]'
search_url = 'https://www.findx.com/{category}?{q}'
type_map = {
    'none': 'web',
    'general': 'web',
    'images': 'images',
    'videos': 'videos',
}


def request(query, params):
    params['url'] = search_url.format(
        category=type_map[params['category']],
        q=urlencode({
            'q': query,
            'page': params['pageno']
        })
    )
    return params


def response(resp):
    dom = html.fromstring(resp.text)
    results_raw_json = dom.xpath(results_xpath)
    results_json = loads(extract_text(results_raw_json))

    if len(results_json['web']['results']) > 0:
        return _general_results(results_json['web']['results'])

    if len(results_json['images']['results']) > 0:
        return _images_results(results_json['images']['results'])

    if len(results_json['video']['results']) > 0:
        return _videos_results(results_json['video']['results'])

    return []


def _general_results(general_results):
    results = []
    for result in general_results:
        results.append({
            'url': result['url'],
            'title': result['title'],
            'content': result['sum'],
        })
    return results


def _images_results(image_results):
    results = []
    for result in image_results:
        results.append({
            'url': result['sourceURL'],
            'title': result['title'],
            'content': result['source'],
            'thumbnail_src': _extract_url(result['assets']['thumb']['url']),
            'img_src': _extract_url(result['assets']['file']['url']),
            'template': 'images.html',
        })
    return results


def _videos_results(video_results):
    results = []
    for result in video_results:
        if not result['kind'].startswith('youtube'):
            logger.warn('Unknown video kind in findx: {}'.format(result['kind']))
            continue

        description = result['snippet']['description']
        if len(description) > 300:
            description = description[:300] + '...'

        results.append({
            'url': base_youtube_url + result['id'],
            'title': result['snippet']['title'],
            'content': description,
            'thumbnail': _extract_url(result['snippet']['thumbnails']['default']['url']),
            'publishedDate': parser.parse(result['snippet']['publishedAt']),
            'embedded': embedded_url.format(videoid=result['id']),
            'template': 'videos.html',
        })
    return results


def _extract_url(url):
    matching = re.search('(/https?://[^)]+)', url)
    if matching:
        return matching.group(0)[1:]
    return ''
