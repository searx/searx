"""
 Deviantart (Images)

 @website     https://www.deviantart.com/
 @provide-api yes (https://www.deviantart.com/developers/) (RSS)

 @using-api   no (TODO, rewrite to api)
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, thumbnail_src, img_src

 @todo        rewrite to api
"""

from urllib import urlencode
from urlparse import urljoin
from lxml import html
import re
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['images']
paging = True

# search-url
base_url = 'https://www.deviantart.com/'
search_url = base_url + 'browse/all/?offset={offset}&{query}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 24

    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    # return empty array if a redirection code is returned
    if resp.status_code == 302:
        return []

    dom = html.fromstring(resp.text)

    regex = re.compile(r'\/200H\/')

    # parse results
    for result in dom.xpath('//div[contains(@class, "tt-a tt-fh")]'):
        link = result.xpath('.//a[contains(@class, "thumb")]')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title_links = result.xpath('.//span[@class="details"]//a[contains(@class, "t")]')
        title = extract_text(title_links[0])
        thumbnail_src = link.xpath('.//img')[0].attrib.get('src')
        img_src = regex.sub('/', thumbnail_src)

        # http to https, remove domain sharding
        thumbnail_src = re.sub(r"https?://(th|fc)\d+.", "https://th01.", thumbnail_src)
        thumbnail_src = re.sub(r"http://", "https://", thumbnail_src)

        url = re.sub(r"http://(.*)\.deviantart\.com/", "https://\\1.deviantart.com/", url)

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'thumbnail_src': thumbnail_src,
                        'template': 'images.html'})

    # return results
    return results
