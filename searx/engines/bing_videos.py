"""
 Bing (Videos)

 @website     https://www.bing.com/videos
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content, thumbnail
"""

from json import loads
from lxml import html
from searx.engines.bing_images import _fetch_supported_languages, supported_languages_url
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode
from searx.utils import match_language


categories = ['videos']
paging = True
safesearch = True
time_range_support = True
number_of_results = 10
language_support = True

search_url = 'https://www.bing.com/videos/asyncv2?{query}&async=content&'\
             'first={offset}&count={number_of_results}&CW=1366&CH=25&FORM=R5VR5'
time_range_string = '&qft=+filterui:videoage-lt{interval}'
time_range_dict = {'day': '1440',
                   'week': '10080',
                   'month': '43200',
                   'year': '525600'}

# safesearch definitions
safesearch_types = {2: 'STRICT',
                    1: 'DEMOTE',
                    0: 'OFF'}


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    # safesearch cookie
    params['cookies']['SRCHHPGUSR'] = \
        'ADLT=' + safesearch_types.get(params['safesearch'], 'DEMOTE')

    # language cookie
    language = match_language(params['language'], supported_languages, language_aliases).lower()
    params['cookies']['_EDGE_S'] = 'mkt=' + language + '&F=1'

    # query and paging
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      number_of_results=number_of_results)

    # time range
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath('//div[@class="dg_u"]'):
        url = result.xpath('./div[@class="mc_vtvc"]/a/@href')[0]
        url = 'https://bing.com' + url
        title = extract_text(result.xpath('./div/a/div/div[@class="mc_vtvc_title"]/@title'))
        content = extract_text(result.xpath('./div/a/div/div/div/div/text()'))
        thumbnail = result.xpath('./div/a/div/div/img/@src')[0]

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': thumbnail,
                        'template': 'videos.html'})

        if len(results) >= number_of_results:
            break

    return results
