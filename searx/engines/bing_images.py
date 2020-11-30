"""
 Bing (Images)

 @website     https://www.bing.com/images
 @provide-api yes (http://datamarket.azure.com/dataset/bing/search),
              max. 5000 query/month

 @using-api   no (because of query limit)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, img_src

"""

from urllib.parse import urlencode
from lxml import html
from json import loads
from searx.utils import match_language

from searx.engines.bing import language_aliases
from searx.engines.bing import _fetch_supported_languages, supported_languages_url  # NOQA

# engine dependent config
categories = ['images']
paging = True
safesearch = True
time_range_support = True
language_support = True
supported_languages_url = 'https://www.bing.com/account/general'
number_of_results = 28

# search-url
base_url = 'https://www.bing.com/'
search_string = 'images/search'\
    '?{query}'\
    '&count={count}'\
    '&first={first}'\
    '&FORM=IBASEP'
time_range_string = '&qft=+filterui:age-lt{interval}'
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
    offset = ((params['pageno'] - 1) * number_of_results) + 1

    search_path = search_string.format(
        query=urlencode({'q': query}),
        count=number_of_results,
        first=offset)

    language = match_language(params['language'], supported_languages, language_aliases).lower()

    params['cookies']['SRCHHPGUSR'] = \
        'ADLT=' + safesearch_types.get(params['safesearch'], 'DEMOTE')

    params['cookies']['_EDGE_S'] = 'mkt=' + language +\
        '&ui=' + language + '&F=1'

    params['url'] = base_url + search_path
    if params['time_range'] in time_range_dict:
        params['url'] += time_range_string.format(interval=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath('//div[@class="imgpt"]'):
        try:
            img_format = result.xpath('./div[contains(@class, "img_info")]/span/text()')[0]
            # Microsoft seems to experiment with this code so don't make the path too specific,
            # just catch the text section for the first anchor in img_info assuming this to be
            # the originating site.
            source = result.xpath('./div[contains(@class, "img_info")]//a/text()')[0]

            m = loads(result.xpath('./a/@m')[0])

            # strip 'Unicode private use area' highlighting, they render to Tux
            # the Linux penguin and a standing diamond on my machine...
            title = m.get('t', '').replace('\ue000', '').replace('\ue001', '')
            results.append({'template': 'images.html',
                            'url': m['purl'],
                            'thumbnail_src': m['turl'],
                            'img_src': m['murl'],
                            'content': '',
                            'title': title,
                            'source': source,
                            'img_format': img_format})
        except:
            continue

    return results
