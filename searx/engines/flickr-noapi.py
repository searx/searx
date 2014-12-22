#!/usr/bin/env python

#  Flickr (Images)
#
# @website     https://www.flickr.com
# @provide-api yes (https://secure.flickr.com/services/api/flickr.photos.search.html)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       url, title, thumbnail, img_src

from urllib import urlencode
from json import loads
import re

categories = ['images']

url = 'https://secure.flickr.com/'
search_url = url+'search/?{query}&page={page}'
photo_url = 'https://www.flickr.com/photos/{userid}/{photoid}'
regex = re.compile(r"\"search-photos-models\",\"photos\":(.*}),\"totalItems\":", re.DOTALL)
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

        # In paged configuration, the first pages' photos are represented by a None object
        if photo is None:
            continue

        img_src = None
        # From the biggest to the lowest format
        for image_size in image_sizes:
            if image_size in photo['sizes']:
                img_src = photo['sizes'][image_size]['displayUrl']
                break

        if not img_src:
            continue

        if 'id' not in photo['owner']:
            continue

        url = build_flickr_url(photo['owner']['id'], photo['id'])

        title = photo['title']

        content = '<span class="photo-author">' + photo['owner']['username'] + '</span><br />'

        if 'description' in photo:
            content = content + '<span class="description">' + photo['description'] + '</span>'

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': content,
                        'template': 'images.html'})

    return results
