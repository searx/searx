#!/usr/bin/env python

## Flickr (Images)
# 
# @website     https://www.flickr.com
# @provide-api yes (https://secure.flickr.com/services/api/flickr.photos.search.html) 
# 
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, thumbnail, img_src
#More info on api-key : https://www.flickr.com/services/apps/create/

from urllib import urlencode
from json import loads

categories = ['images']

nb_per_page = 15
paging = True
api_key= None


url = 'https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key={api_key}&{text}&sort=relevance&extras=description%2C+owner_name%2C+url_o%2C+url_z&per_page={nb_per_page}&format=json&nojsoncallback=1&page={page}'
photo_url = 'https://www.flickr.com/photos/{userid}/{photoid}'

paging = True

def build_flickr_url(user_id, photo_id):
    return photo_url.format(userid=user_id,photoid=photo_id)


def request(query, params):
    params['url'] = url.format(text=urlencode({'text': query}),
                               api_key=api_key,
                               nb_per_page=nb_per_page,
                               page=params['pageno'])
    return params


def response(resp):
    results = []
    
    search_results = loads(resp.text)

    # return empty array if there are no results
    if not 'photos' in search_results:
        return []

    if not 'photo' in search_results['photos']:
        return []

    photos = search_results['photos']['photo']

    # parse results
    for photo in photos:
        if 'url_o' in photo:
            img_src = photo['url_o']
        elif 'url_z' in photo:
            img_src = photo['url_z']
        else:
            continue

        url = build_flickr_url(photo['owner'], photo['id'])

        title = photo['title']
        
        content = '<span class="photo-author">'+ photo['ownername'] +'</span><br />'
        
        content = content + '<span class="description">' + photo['description']['_content'] + '</span>'
        
        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': content,
                        'template': 'images.html'})

    # return results
    return results
