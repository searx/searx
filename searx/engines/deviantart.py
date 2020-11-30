"""
 Deviantart (Images)

 @website     https://www.deviantart.com/
 @provide-api yes (https://www.deviantart.com/developers/) (RSS)

 @using-api   no (TODO, rewrite to api)
 @results     HTML
 @stable      no (HTML can change)
 @parse       url, title, img_src

 @todo        rewrite to api
"""
# pylint: disable=missing-function-docstring

from urllib.parse import urlencode
from lxml import html

# engine dependent config
categories = ['images']
paging = True
time_range_support = True

time_range_dict = {
    'day': 'popular-24-hours',
    'week': 'popular-1-week',
    'month': 'popular-1-month',
    'year': 'most-recent',
}

# search-url
base_url = 'https://www.deviantart.com'

def request(query, params):

    # https://www.deviantart.com/search/deviations?page=5&q=foo

    query =  {
        'page' : params['pageno'],
        'q'    : query,
    }
    if params['time_range'] in time_range_dict:
        query['order'] = time_range_dict[params['time_range']]

    params['url'] = base_url + '/search/deviations?' + urlencode(query)

    return params

def response(resp):

    results = []

    dom = html.fromstring(resp.text)

    for row in dom.xpath('//div[contains(@data-hook, "content_row")]'):
        for result in row.xpath('./div'):

            a_tag = result.xpath('.//a[@data-hook="deviation_link"]')[0]
            noscript_tag = a_tag.xpath('.//noscript')

            if noscript_tag:
                img_tag = noscript_tag[0].xpath('.//img')
            else:
                img_tag = a_tag.xpath('.//img')
            if not img_tag:
                continue
            img_tag = img_tag[0]

            results.append({
                'template': 'images.html',
                'url': a_tag.attrib.get('href'),
                'img_src': img_tag.attrib.get('src'),
                'title': img_tag.attrib.get('alt'),
            })

    return results
