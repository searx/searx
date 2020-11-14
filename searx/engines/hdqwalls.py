# -*- coding: utf-8 -*-

"""
 HDQwalls (Images)
 @website     https://hdqwalls.com/
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @parse       url, title
"""

from lxml import html
from searx.utils import extract_text
from searx.poolrequests import get
from urllib.parse import quote, urlencode

categories = ['images']
paging = True
spacechr = '+'

# search-url
base_url = 'https://hdqwalls.com'
search_url = base_url + '/search?q={query}&page={pageno}'

results_xpath = '//div[contains(@class,"wall-resp")]/a/img'
url_xpath =           '../@href'
title_xpath =         '../@alt'
thumbnail_src_xpath = './@src'

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
        url =  base_url + extract_text(result_dom.xpath(url_xpath))
        title =  extract_text(result_dom.xpath(title_xpath))
        thumbnail_src = extract_text(result_dom.xpath(thumbnail_src_xpath))
        img_src = thumbnail_src.replace('/thumb/','/')

        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'thumbnail_src': thumbnail_src,
                        'img_src': img_src})

    # return results
    return results
