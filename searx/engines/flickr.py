#!/usr/bin/env python

from urllib import quote
from lxml import html
from urlparse import urljoin

categories = ['images']

base_url = 'https://secure.flickr.com/'
search_url = base_url+'search/?q='

def request(query, params):
    global search_url
    query = quote(query.replace(' ', '+'), safe='+')
    params['url'] = search_url + query
    return params

def response(resp):
    global base_url
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath('//div[@id="thumbnails"]//a[@class="rapidnofollow photo-click" and @data-track="photo-click"]'):
        url = urljoin(base_url, result.attrib.get('href'))
        img = result.xpath('.//img')[0]
        title = img.attrib.get('alt', '')
        img_src = img.attrib.get('data-defer-src')
        if not img_src:
            continue
        results.append({'url': url, 'title': title, 'img_src': img_src, 'template': 'images.html'})
    return results
