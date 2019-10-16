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
from urllib.parse import urlencode
from searx.engines.bing_images import _fetch_supported_languages, supported_languages_url
from searx.utils import match_language, html_fromstring


categories = ['videos']
paging = True
safesearch = True
time_range_support = True
number_of_results = 28
language_support = True

base_url = 'https://www.bing.com/'
search_string = 'videos/search'\
    '?{query}'\
    '&count={count}'\
    '&first={first}'\
    '&scope=video'\
    '&FORM=QBLH'
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
async def request(query, params):
    offset = ((params['pageno'] - 1) * number_of_results) + 1

    search_path = search_string.format(
        query=urlencode({'q': query}),
        count=number_of_results,
        first=offset)

    # safesearch cookie
    params['cookies']['SRCHHPGUSR'] = \
        'ADLT=' + safesearch_types.get(params['safesearch'], 'DEMOTE')

    # language cookie
    language = match_language(params['language'], supported_languages, language_aliases).lower()
    params['cookies']['_EDGE_S'] = 'mkt=' + language + '&F=1'

    # query and paging
    params['url'] = base_url + search_path

    # time range
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
async def response(resp):
    results = []

    dom = await html_fromstring(resp.text)

    for result in dom.xpath('//div[@class="dg_u"]'):
        try:
            metadata = loads(result.xpath('.//div[@class="vrhdata"]/@vrhm')[0])
            info = ' - '.join(result.xpath('.//div[@class="mc_vtvc_meta_block"]//span/text()')).strip()
            content = '{0} - {1}'.format(metadata['du'], info)
            thumbnail = '{0}th?id={1}'.format(base_url, metadata['thid'])
            results.append({'url': metadata['murl'],
                            'thumbnail': thumbnail,
                            'title': metadata.get('vt', ''),
                            'content': content,
                            'template': 'videos.html'})

        except:
            continue

    return results
