"""
 500px (Images)

 @website     https://500px.com
 @provide-api yes (https://developers.500px.com/)

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, thumbnail, img_src, content

 @todo        rewrite to api
"""

from json import loads
from searx.url_utils import urlencode, urljoin

# engine dependent config
categories = ['images']
paging = True

# search-url
base_url = 'https://500px.com'
search_url = 'https://api.500px.com/v1/photos/search?type=photos'\
    '&{query}'\
    '&image_size%5B%5D=4'\
    '&image_size%5B%5D=20'\
    '&image_size%5B%5D=21'\
    '&image_size%5B%5D=1080'\
    '&image_size%5B%5D=1600'\
    '&image_size%5B%5D=2048'\
    '&include_states=true'\
    '&formats=jpeg%2Clytro'\
    '&include_tags=true'\
    '&exclude_nude=true'\
    '&page={pageno}'\
    '&rpp=50'\
    '&sdk_key=b68e60cff4c929bedea36ca978830c5caca790c3'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'term': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    response_json = loads(resp.text)

    # parse results
    for result in response_json['photos']:
        url = urljoin(base_url, result['url'])
        title = result['name']
        # last index is the biggest resolution
        img_src = result['image_url'][-1]
        thumbnail_src = result['image_url'][0]
        content = result['description'] or ''

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': content,
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
