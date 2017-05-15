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
import re
from searx.url_utils import urlencode, urljoin

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

    # get links from result-text
    regex = re.compile('(</a>|<a)')
    results_parts = re.split(regex, resp.text)

    cur_element = ''

    # iterate over link parts
    for result_part in results_parts:
        # processed start and end of link
        if result_part == '<a':
            cur_element = result_part
            continue
        elif result_part != '</a>':
            cur_element += result_part
            continue

        cur_element += result_part

        # fix xml-error
        cur_element = cur_element.replace('"></a>', '"/></a>')

        dom = html.fromstring(cur_element)
        link = dom.xpath('//a')[0]

        url = urljoin(base_url, link.attrib.get('href'))
        title = link.attrib.get('title', '')

        thumbnail_src = urljoin(base_url, link.xpath('.//img')[0].attrib['src'])
        # TODO: get image with higher resolution
        img_src = thumbnail_src

        # check if url is showing to a photo
        if '/photo/' not in url:
            continue

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': '',
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
