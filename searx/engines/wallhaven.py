# -*- coding: utf-8 -*-

"""
 Wallhaven (Images)
 @website     http://wallhaven.cc/
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @parse       url, content
"""

from lxml import html
import re
from searx.poolrequests import get
from urllib.parse import quote, urlencode
from searx.utils import extract_text
from urllib import parse

categories = ['images']
paging = True

# search-url
base_url = 'https://wallhaven.cc'
search_url = base_url + '/search?q={query}&page={pageno}'
spacechr = '+'

results_xpath = '//div[contains(@id,"thumbs")]/section[contains(@class,"thumb-listing-page")]/ul/li/figure[contains(@class,"thumb")]'
id_xpath =            './@data-wallpaper-id'
url_xpath =           './a/@href'
png_check_xpath =     './div[contains(@class,"thumb-info")]/span[contains(@class,"png")]/@class'
thumbnail_src_xpath = './img/@data-src'

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
        url =  extract_text(result_dom.xpath(url_xpath))
        id =  extract_text(result_dom.xpath(id_xpath))
        thumbnail_src = extract_text(result_dom.xpath(thumbnail_src_xpath))
        png_check = extract_text(result_dom.xpath(png_check_xpath))
        if png_check == 'png':
             img_src = thumbnail_src.replace('th.wallhaven.cc/small/','w.wallhaven.cc/full/').replace('/' + id + '.jpg','/wallhaven-' + id + '.png')
        else:
             img_src = thumbnail_src.replace('th.wallhaven.cc/small/','w.wallhaven.cc/full/').replace('/' + id,'/wallhaven-' + id)

        results.append({'template': 'images.html',
                        'url': url,
                        'id': id,
                        'title': 'Wallhaven ' + id,
                        'thumbnail_src': thumbnail_src,
                        'img_src': img_src})

    # return results
    return results
