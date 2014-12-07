## Deviantart (Images)
#
# @website     https://www.deviantart.com/
# @provide-api yes (https://www.deviantart.com/developers/) (RSS)
#
# @using-api   no (TODO, rewrite to api)
# @results     HTML
# @stable      no (HTML can change)
# @parse       url, title, thumbnail, img_src
#
# @todo        rewrite to api

from urllib import urlencode
from urlparse import urljoin
from lxml import html

# engine dependent config
categories = ['images']
paging = True

# search-url
base_url = 'https://www.deviantart.com/'
search_url = base_url+'search?offset={offset}&{query}'


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

    # parse results
    for result in dom.xpath('//div[contains(@class, "tt-a tt-fh")]'):
        link = result.xpath('.//a[contains(@class, "thumb")]')[0]
        url = urljoin(base_url, link.attrib.get('href'))
        title_links = result.xpath('.//span[@class="details"]//a[contains(@class, "t")]')  # noqa
        title = ''.join(title_links[0].xpath('.//text()'))
        img_src = link.xpath('.//img')[0].attrib['src']

        # append result
        results.append({'url': url,
                        'title': title,
                        'img_src': img_src,
                        'template': 'images.html'})

    # return results
    return results
