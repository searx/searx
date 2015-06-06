#!/usr/bin/env python

"""
  Flickr (Images)

 @website     https://www.flickr.com
 @provide-api yes (https://secure.flickr.com/services/api/flickr.photos.search.html)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, thumbnail, img_src
"""

from urllib import urlencode
from json import loads
import re
from searx.engines import logger


logger = logger.getChild('flickr-noapi')

categories = ['images']

url = 'https://www.flickr.com/'
search_url = url + 'search?{query}&page={page}'
photo_url = 'https://www.flickr.com/photos/{userid}/{photoid}'
regex = re.compile(r"\"search-photos-lite-models\",\"photos\":(.*}),\"totalItems\":", re.DOTALL)
image_sizes = ('o', 'k', 'h', 'b', 'c', 'z', 'n', 'm', 't', 'q', 's')

paging = True


def build_flickr_url(user_id, photo_id):
    return photo_url.format(userid=user_id, photoid=photo_id)


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'text': query}),
                                      page=params['pageno'])

    return params


def response(resp):
    results = []

    matches = regex.search(resp.text)

    if matches is None:
        return results

    match = matches.group(1)
    search_results = loads(match)

    if '_data' not in search_results:
        return []

    photos = search_results['_data']

    for photo in photos:

        # In paged configuration, the first pages' photos
        # are represented by a None object
        if photo is None:
            continue

        img_src = None
        # From the biggest to the lowest format
        for image_size in image_sizes:
            if image_size in photo['sizes']:
                img_src = photo['sizes'][image_size]['url']
                break

        if not img_src:
            logger.debug('cannot find valid image size: {0}'.format(repr(photo)))
            continue

        if 'ownerNsid' not in photo:
            continue

        # For a bigger thumbnail, keep only the url_z, not the url_n
        if 'n' in photo['sizes']:
            thumbnail_src = photo['sizes']['n']['url']
        elif 'z' in photo['sizes']:
            thumbnail_src = photo['sizes']['z']['url']
        else:
            thumbnail_src = img_src

        url = build_flickr_url(photo['ownerNsid'], photo['id'])

        title = photo.get('title', '')

        content = '<span class="photo-author">' +\
                  photo['username'] +\
                  '</span><br />'

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'thumbnail_src': thumbnail_src,
                        'content': content,
                        'template': 'images.html'})

    return results
