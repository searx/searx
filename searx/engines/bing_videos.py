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
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode


categories = ['videos']
paging = True
safesearch = True
time_range_support = True
number_of_results = 10

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
    params['cookies']['_EDGE_S'] = 'mkt=' + params['language'].lower() + '&F=1'

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

        # try to extract the url
        url_container = result.xpath('.//div[@class="sa_wrapper"]/@data-eventpayload')
        if len(url_container) > 0:
            url = loads(url_container[0])['purl']
        else:
            url = result.xpath('./a/@href')[0]

            # discard results that do not return an external url
            # very recent results sometimes don't return the video's url
            if url.startswith('/videos/search?'):
                continue

        title = extract_text(result.xpath('./a//div[@class="tl"]'))
        content = extract_text(result.xpath('.//div[@class="pubInfo"]'))
        thumbnail = result.xpath('.//div[@class="vthumb"]/img/@src')[0]

        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': thumbnail,
                        'template': 'videos.html'})

        # first page ignores requested number of results
        if len(results) >= number_of_results:
            break

    return results
