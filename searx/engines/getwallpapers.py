# -*- coding: utf-8 -*-

"""
 GetWallpapers (Images)
 @website     http://getwallpapers.com/
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @parse       url, title
"""

from lxml import html
from searx.poolrequests import get
from urllib.parse import quote, urlencode
from searx.utils import extract_text

paging = True
spacechr = '+'

categories = ['images']

# search-url
base_url = 'http://getwallpapers.com'
search_url = base_url + '/search?term={query}&page={pageno}'

results_xpath = '//div[@class="column collection_thumb"]'
url_xpath =           './a/@href'
title_xpath =         './a/@title'
thumbnail_src_xpath = './a/img/@data-src'

# do search-request
def request(query, params):
    params['url'] = search_url.format(query=quote(query), pageno=params['pageno']).replace('%20',spacechr)
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
        url = extract_text(result_dom.xpath(url_xpath))
        title =  extract_text(result_dom.xpath(title_xpath))
        thumbnail_src = base_url + extract_text(result_dom.xpath(thumbnail_src_xpath))

        img_src = thumbnail_src.replace('/wallpaper/small-retina/','/wallpaper/full/')

        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'thumbnail_src': thumbnail_src,
                        'img_src': img_src})

    # return results
    return results
