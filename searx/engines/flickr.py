#!/usr/bin/env python

from urllib import urlencode
#from json import loads
from urlparse import urljoin
from lxml import html
from time import time

categories = ['images']

url = 'https://secure.flickr.com/'
search_url = url+'search/?{query}&page={page}'
results_xpath = '//div[@class="view display-item-tile"]/figure/div'

paging = True


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'text': query}),
                                      page=params['pageno'])
    time_string = str(int(time())-3)
    params['cookies']['BX'] = '3oqjr6d9nmpgl&b=3&s=dh'
    params['cookies']['xb'] = '421409'
    params['cookies']['localization'] = 'en-us'
    params['cookies']['flrbp'] = time_string +\
        '-3a8cdb85a427a33efda421fbda347b2eaf765a54'
    params['cookies']['flrbs'] = time_string +\
        '-ed142ae8765ee62c9ec92a9513665e0ee1ba6776'
    params['cookies']['flrb'] = '9'
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    for result in dom.xpath(results_xpath):
        img = result.xpath('.//img')

        if not img:
            continue

        img = img[0]
        img_src = 'https:'+img.attrib.get('src')

        if not img_src:
            continue

        href = urljoin(url, result.xpath('.//a')[0].attrib.get('href'))
        title = img.attrib.get('alt', '')
        results.append({'url': href,
                        'title': title,
                        'img_src': img_src,
                        'template': 'images.html'})
    return results
