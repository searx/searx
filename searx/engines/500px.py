## 500px (Images)
#
# @website     https://500px.com
# @provide-api yes (https://developers.500px.com/)
#
# @using-api   no
# @results     HTML
# @stable      no (HTML can change)
# @parse       url, title, thumbnail, img_src, content
#
# @todo        rewrite to api

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urlencode
from urllib.parse import urljoin
from lxml import html
import re

# engine dependent config
categories = ['images']
paging = True

# search-url
base_url = 'https://500px.com'
search_url = base_url+'/search?search?page={pageno}&type=photos&{query}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'],
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)
    regex = re.compile('3\.jpg.*$')

    # parse results
    for result in dom.xpath('//div[@class="photo"]'):
        link = result.xpath('.//a')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title = result.xpath('.//div[@class="title"]//text()')[0]
        thumbnail_src = link.xpath('.//img')[0].attrib['src']
        # To have a bigger thumbnail, uncomment the next line
        #thumbnail_src = regex.sub('4.jpg', thumbnail_src)
        content = result.xpath('.//div[@class="info"]//text()')[0]
        img_src = regex.sub('2048.jpg', thumbnail_src)

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'content': content,
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
