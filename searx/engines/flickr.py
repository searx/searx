#!/usr/bin/env python

from urllib import urlencode
from lxml import html
from urlparse import urljoin

categories = ['images']

url = 'https://secure.flickr.com/'
search_url = url+'search/?{query}&page={page}'
results_xpath = '//div[@id="thumbnails"]//a[@class="rapidnofollow photo-click" and @data-track="photo-click"]'  # noqa

paging = True


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      page=params['pageno'])
    return params


def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath(results_xpath):
        href = urljoin(url, result.attrib.get('href'))
        img = result.xpath('.//img')[0]
        title = img.attrib.get('alt', '')
        img_src = img.attrib.get('data-defer-src')
        if not img_src:
            continue
        results.append({'url': href,
                        'title': title,
                        'img_src': img_src,
                        'template': 'images.html'})
    return results
