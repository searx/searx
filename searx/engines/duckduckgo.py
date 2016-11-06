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

from urllib import urlencode
from lxml.html import fromstring
from requests import get
from json import loads
from searx.engines.xpath import extract_text

# engine dependent config
categories = ['general']
paging = True
language_support = True
supported_languages_url = 'https://duckduckgo.com/d2030.js'
time_range_support = True

# search-url
url = 'https://duckduckgo.com/html?{query}&s={offset}'
time_range_url = '&df={range}'

time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}

# specific xpath variables
result_xpath = '//div[@class="result results_links results_links_deep web-result "]'  # noqa
url_xpath = './/a[@class="result__a"]/@href'
title_xpath = './/a[@class="result__a"]'
content_xpath = './/a[@class="result__snippet"]'


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * 30

    # custom fixes for languages
    if params['language'] == 'all':
        locale = None
    elif params['language'][:2] == 'ja':
        locale = 'jp-jp'
    elif params['language'] == 'zh-TW':
        locale = 'tw-tzh'
    elif params['language'] == 'zh-HK':
        locale = 'hk-tzh'
    elif params['language'][-2:] == 'SA':
        locale = 'xa' + params['language'].split('-')[0]
    elif params['language'][-2:] == 'GB':
        locale = 'uk' + params['language'].split('-')[0]
    else:
        locale = params['language'].split('-')
        if len(locale) == 2:
            # country code goes first
            locale = locale[1].lower() + '-' + locale[0].lower()
        else:
            # tries to get a country code from language
            locale = locale[0].lower()
            for lc in supported_languages:
                lc = lc.split('-')
                if locale == lc[0]:
                    locale = lc[1].lower() + '-' + lc[0].lower()
                    break

    if locale:
        params['url'] = url.format(
            query=urlencode({'q': query, 'kl': locale}), offset=offset)
    else:
        params['url'] = url.format(
            query=urlencode({'q': query}), offset=offset)

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
def fetch_supported_languages():
    response = get(supported_languages_url)

    # response is a js file with regions as an embedded object
    response_page = response.text
    response_page = response_page[response_page.find('regions:{') + 8:]
    response_page = response_page[:response_page.find('}') + 1]

    regions_json = loads(response_page)
    supported_languages = map((lambda x: x[3:] + '-' + x[:2].upper()), regions_json.keys())

    return supported_languages
