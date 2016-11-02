"""
 Bing (Images)

 @website     https://www.bing.com/images
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, img_src

 @todo        currently there are up to 35 images receive per page,
              because bing does not parse count=10.
              limited response to 10 images
"""

from urllib import urlencode
from lxml import html
from json import loads
import re

# engine dependent config
categories = ['images']
paging = True
safesearch = True
time_range_support = True

# search-url
base_url = 'https://www.bing.com/'
search_string = 'images/search?{query}&count=10&first={offset}'
time_range_string = '&qft=+filterui:age-lt{interval}'
thumb_url = "https://www.bing.com/th?id={ihk}"
time_range_dict = {'day': '1440',
                   'week': '10080',
                   'month': '43200'}

# safesearch definitions
safesearch_types = {2: 'STRICT',
                    1: 'DEMOTE',
                    0: 'OFF'}


_quote_keys_regex = re.compile('({|,)([a-z][a-z0-9]*):(")', re.I | re.U)


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    # required for cookie
    if params['language'] == 'all':
        language = 'en-US'
    else:
        language = params['language'].replace('_', '-')

    search_path = search_string.format(
        query=urlencode({'q': query}),
        offset=offset)

    params['cookies']['SRCHHPGUSR'] = \
        'NEWWND=0&NRSLT=-1&SRCHLANG=' + language.split('-')[0] +\
        '&ADLT=' + safesearch_types.get(params['safesearch'], 'DEMOTE')

    params['url'] = base_url + search_path
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@class="dg_u"]/div'):
        link = result.xpath('./a')[0]

        # parse json-data (it is required to add a space, to make it parsable)
        json_data = loads(_quote_keys_regex.sub(r'\1"\2": \3', link.attrib.get('m')))

        title = link.attrib.get('t1')
        ihk = link.attrib.get('ihk')

        # url = 'http://' + link.attrib.get('t3')
        url = json_data.get('surl')
        img_src = json_data.get('imgurl')

        # append result
        results.append({'template': 'images.html',
                        'url': url,
                        'title': title,
                        'content': '',
                        'thumbnail_src': thumb_url.format(ihk=ihk),
                        'img_src': img_src})

        # TODO stop parsing if 10 images are found
        if len(results) >= 10:
            break

    # return results
    return results
