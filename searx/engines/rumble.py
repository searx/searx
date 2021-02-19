# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Wikipedia (Web
"""
from urllib.parse import urlencode
from lxml import html
from datetime import datetime

# about
from searx.utils import extract_text

about = {
    "website": 'https://rumble.com/',
    "wikidata_id": 'Q104765127',
    "official_api_documentation": 'https://help.rumble.com/',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['videos']
paging = True

# search-url
base_url = 'https://rumble.com'
# https://rumble.com/search/video?q=searx&page=3
search_url = base_url + '/search/video?{query}&page={pageno}'

# cats
# https://rumble.com/embed/vkgt9/?pub=7h2v5   iframe url
# <iframe class="rumble" width="640" height="360" src="https://rumble.com/embed/vkgt9/?pub=7h2v5" frameborder="0" allowfullscreen></iframe>
embedded_url = '<iframe class="rumble" width="640" height="360" src="https://rumble.com/embed/v{video_id}/?pub=7h2v5 ' \
               'frameborder="0" allowfullscreen></iframe>'

url_xpath = './/a[@class="video-item--a"]/@href'
thumbnail_xpath = './/img[@class="video-item--img"]/@src'
title_xpath = './/h3[@class="video-item--title"]'
published_date = './/time[@class="video-item--meta video-item--time"]/@datetime'
earned_xpath = './/span[@class="video-item--meta video-item--earned"]/@data-value'
views_xpath = './/span[@class="video-item--meta video-item--views"]/@data-value'
rumbles_xpath = './/span[@class="video-item--meta video-item--rumbles"]/@data-value'
author_xpath = './/div[@class="ellipsis-1"]'
length_xpath = './/span[@class="video-item--duration"]/@data-value'


# do search-request
def request(query, params):
    params['url'] = search_url.format(pageno=params['pageno'], query=urlencode({'q': query}))
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    results_dom = dom.xpath('//li[contains(@class, "video-listing-entry")]')

    if not results_dom:
        return []

    for result_dom in results_dom:
        url = base_url + extract_text(result_dom.xpath(url_xpath))
        thumbnail = extract_text(result_dom.xpath(thumbnail_xpath))
        title = extract_text(result_dom.xpath(title_xpath))
        p_date = extract_text(result_dom.xpath(published_date))
        # fix offset date for line 644 webapp.py check
        fixed_date = datetime.strptime(p_date, '%Y-%m-%dT%H:%M:%S%z')
        earned = extract_text(result_dom.xpath(earned_xpath))
        views = extract_text(result_dom.xpath(views_xpath))
        rumbles = extract_text(result_dom.xpath(rumbles_xpath))
        author = extract_text(result_dom.xpath(author_xpath))
        length = extract_text(result_dom.xpath(length_xpath))
        if earned:
            content = f"{views} views - {rumbles} rumbles - ${earned}"
        else:
            content = f"{views} views - {rumbles} rumbles"

        # TODO follow url to get embedded video_id
        # add 'embedded': embedded, to results

        results.append({
            'url': url,
            'title': title,
            'content': content,
            'author': author,
            'length': length,
            'template': 'videos.html',
            'publishedDate': fixed_date,
            'thumbnail': thumbnail,
        })
    return results

