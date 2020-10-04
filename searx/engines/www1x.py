"""
 1x (Images)

 @website     http://1x.com/
 @provide-api no

 @using-api   no
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, thumbnail, img_src, content
"""

from lxml import html
from urllib.parse import urlencode, urljoin
from searx.utils import extract_text

# engine dependent config
categories = ['images']
paging = False

# search-url
base_url = 'https://1x.com'
search_url = base_url + '/backend/search.php?{query}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)
    for res in dom.xpath('//div[@class="List-item MainListing"]'):
        # processed start and end of link
        link = res.xpath('//a')[0]

        url = urljoin(base_url, link.attrib.get('href'))
        title = extract_text(link)

        thumbnail_src = urljoin(base_url, res.xpath('.//img')[0].attrib['src'])
        # TODO: get image with higher resolution
        img_src = thumbnail_src

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': '',
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
