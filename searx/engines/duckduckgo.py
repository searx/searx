"""
 DuckDuckGo (Web)

 @website     https://duckduckgo.com/
 @provide-api yes (https://duckduckgo.com/api),
              but not all results from search-site

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content

 @todo        rewrite to api
"""

from lxml.html import fromstring
from json import loads
from searx.engines.xpath import extract_text
from searx.poolrequests import get
from searx.url_utils import urlencode

# engine dependent config
categories = ['general']
paging = True
language_support = True
supported_languages_url = 'https://duckduckgo.com/d2030.js'
time_range_support = True

# search-url
url = 'https://duckduckgo.com/html?{query}&s={offset}&api=/d.js&o=json&dc={dc_param}'
time_range_url = '&df={range}'

time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}

# specific xpath variables
result_xpath = '//div[@class="result results_links results_links_deep web-result "]'  # noqa
url_xpath = './/a[@class="result__a"]/@href'
title_xpath = './/a[@class="result__a"]'
content_xpath = './/a[@class="result__snippet"]'


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    # custom fixes for languages
    if lang == 'all':
        region_code = None
    elif lang[:2] == 'ja':
        region_code = 'jp-jp'
    elif lang[:2] == 'sl':
        region_code = 'sl-sl'
    elif lang == 'zh-TW':
        region_code = 'tw-tzh'
    elif lang == 'zh-HK':
        region_code = 'hk-tzh'
    elif lang[-2:] == 'SA':
        region_code = 'xa-' + lang.split('-')[0]
    elif lang[-2:] == 'GB':
        region_code = 'uk-' + lang.split('-')[0]
    else:
        region_code = lang.split('-')
        if len(region_code) == 2:
            # country code goes first
            region_code = region_code[1].lower() + '-' + region_code[0].lower()
        else:
            # tries to get a country code from language
            region_code = region_code[0].lower()
            for lc in (lang_list or supported_languages):
                lc = lc.split('-')
                if region_code == lc[0]:
                    region_code = lc[1].lower() + '-' + lc[0].lower()
                    break
    return region_code


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * 30

    region_code = get_region_code(params['language'])
    if region_code:
        params['url'] = url.format(
            query=urlencode({'q': query, 'kl': region_code}), offset=offset, dc_param=offset)
    else:
        params['url'] = url.format(
            query=urlencode({'q': query}), offset=offset, dc_param=offset)

    if params['time_range'] in time_range_dict:
        params['url'] += time_range_url.format(range=time_range_dict[params['time_range']])

    return params


# get response from search-request
def response(resp):
    results = []

    doc = fromstring(resp.text)

    # parse results
    for r in doc.xpath(result_xpath):
        try:
            res_url = r.xpath(url_xpath)[-1]
        except:
            continue

        if not res_url:
            continue

        title = extract_text(r.xpath(title_xpath))
        content = extract_text(r.xpath(content_xpath))

        # append result
        results.append({'title': title,
                        'content': content,
                        'url': res_url})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):

    # response is a js file with regions as an embedded object
    response_page = resp.text
    response_page = response_page[response_page.find('regions:{') + 8:]
    response_page = response_page[:response_page.find('}') + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + '-' + x[:2].upper()), regions_json.keys())

    return supported_languages
