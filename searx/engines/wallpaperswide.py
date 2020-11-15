# -*- coding: utf-8 -*-

"""
 Wallpapers Wide (Images)
 @website     http://wallpaperswide.com/
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @parse       url, title, content
"""

from lxml import html
import re
from searx.poolrequests import get
from urllib.parse import quote, urlencode
from searx.utils import extract_text

categories = ['images']
paging = True

# search-url
base_url = 'http://wallpaperswide.com'
search_url = base_url + '/search/page/{pageno}?q={query}'

results_xpath = '//ul[@class="wallpapers"]/li[@class="wall"]'
url_xpath =              './div[@class="thumb"]/div[@id="hudtitle"]/a/@href'
title_xpath =            './div[@class="thumb"]/div[@id="hudtitle"]/a/@title'
thumbnail_src_xpath =    './div[@class="thumb"]/div[@itemprop="image"]/a/img/@src'
thumbnail_srcalt_xpath = './div[@class="thumb"]/a/img/@src'

# do search-request
def request(query, params):
    params['url'] = search_url.format(query=quote(query), pageno=params['pageno'])
    return params


# get response from search-request
def response(resp):
    results = []
    # return empty array if a redirection code is returned
    if resp.status_code == 302:
        return []

    dom = html.fromstring(resp.text)
    results_dom = dom.xpath(results_xpath)

    if not results_dom:
        return []

    for result_dom in results_dom:
        url =  base_url + '/' + extract_text(result_dom.xpath(url_xpath))
        title =  extract_text(result_dom.xpath(title_xpath))
        thumbnail_srcalt = extract_text(result_dom.xpath(thumbnail_srcalt_xpath))
        if thumbnail_srcalt:
            thumbnail_src = thumbnail_srcalt.replace('-t1.','-t2.')
        else:
            thumbnail_src = extract_text(result_dom.xpath(thumbnail_src_xpath)).replace('-t1.','-t2.')

        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'thumbnail_src': thumbnail_src,
                        'img_src': thumbnail_src})

    # return results
    return results
