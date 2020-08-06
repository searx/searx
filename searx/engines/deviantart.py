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

from lxml import html
import re
from urllib.parse import urlencode
from searx.engines.xpath import extract_text


# engine dependent config
categories = ['images']
paging = True
time_range_support = True

# search-url
base_url = 'https://www.deviantart.com/'
search_url = base_url + 'search?page={page}&{query}'
time_range_url = '&order={range}'

time_range_dict = {'day': 11,
                   'week': 14,
                   'month': 15}


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    params['url'] = search_url.format(page=params['pageno'],
                                      query=urlencode({'q': query}))
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_url.format(range=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    # return empty array if a redirection code is returned
    if resp.status_code == 302:
        return []

    dom = html.fromstring(resp.text)

    # parse results
    for row in dom.xpath('//div[contains(@data-hook, "content_row")]'):
        for result in row.xpath('./div'):
            link = result.xpath('.//a[@data-hook="deviation_link"]')[0]
            url = link.attrib.get('href')
            title = link.attrib.get('title')
            thumbnail_src = result.xpath('.//img')[0].attrib.get('src')
            img_src = thumbnail_src

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
