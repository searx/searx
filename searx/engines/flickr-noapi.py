#!/usr/bin/env python

## Flickr (Images)
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
from urlparse import urljoin
from lxml import html
import re

categories = ['images']

url = 'https://secure.flickr.com/'
search_url = url+'search/?{query}&page={page}'
photo_url = 'https://www.flickr.com/photos/{userid}/{photoid}'
regex = re.compile(r"\"search-photos-models\",\"photos\":(.*}),\"totalItems\":", re.DOTALL)

paging = True

def build_flickr_url(user_id, photo_id):
    return photo_url.format(userid=user_id,photoid=photo_id)


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'text': query}),
                                      page=params['pageno'])
    return params


def response(resp):
    results = []
    
    matches = regex.search(resp.text)
    
    if matches == None:
        return results

    match = matches.group(1)
    search_results = loads(match)
    
    if not '_data' in search_results:
        return []
    
    photos = search_results['_data']
    
    for photo in photos:
        
        # In paged configuration, the first pages' photos are represented by a None object
        if photo == None:
            continue
        
        # From the biggest to the lowest format
        if 'o' in photo['sizes']:
            img_src = photo['sizes']['o']['displayUrl']
        elif 'k' in photo['sizes']:
            img_src = photo['sizes']['k']['displayUrl']
        elif 'h' in photo['sizes']:
            img_src = photo['sizes']['h']['displayUrl']
        elif 'b' in photo['sizes']:
            img_src = photo['sizes']['b']['displayUrl']
        elif 'c' in photo['sizes']:
            img_src = photo['sizes']['c']['displayUrl']
        elif 'z' in photo['sizes']:
            img_src = photo['sizes']['z']['displayUrl']
        elif 'n' in photo['sizes']:
            img_src = photo['sizes']['n']['displayUrl']
        elif 'm' in photo['sizes']:
            img_src = photo['sizes']['m']['displayUrl']
        elif 't' in photo['sizes']:
            img_src = photo['sizes']['to']['displayUrl']
        elif 'q' in photo['sizes']:
            img_src = photo['sizes']['q']['displayUrl']
        elif 's' in photo['sizes']:
            img_src = photo['sizes']['s']['displayUrl']
        else:
            continue
        
        url = build_flickr_url(photo['owner']['id'], photo['id'])

        title = photo['title']
        
        content = '<span class="photo-author">'+ photo['owner']['username'] +'</span><br />'
        
        if 'description' in photo:
            content = content + '<span class="description">' + photo['description'] + '</span>'

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': content,
                        'template': 'images.html'})
        
    return results
