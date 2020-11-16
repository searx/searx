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
from searx.utils import extract_text, match_language, eval_xpath

# engine dependent config
categories = ['general']
paging = False
language_support = True
supported_languages_url = 'https://duckduckgo.com/util/u172.js'
time_range_support = True

language_aliases = {
    'ar-SA': 'ar-XA',
    'es-419': 'es-XL',
    'ja': 'jp-JP',
    'ko': 'kr-KR',
    'sl-SI': 'sl-SL',
    'zh-TW': 'tzh-TW',
    'zh-HK': 'tzh-HK'
}

# search-url
url = 'https://html.duckduckgo.com/html'
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}

# specific xpath variables
result_xpath = '//div[@class="result results_links results_links_deep web-result "]'  # noqa
url_xpath = './/a[@class="result__a"]/@href'
title_xpath = './/a[@class="result__a"]'
content_xpath = './/a[@class="result__snippet"]'
correction_xpath = '//div[@id="did_you_mean"]//a'


# match query's language to a region code that duckduckgo will accept
def get_region_code(lang, lang_list=None):
    if lang == 'all':
        return None

    lang_code = match_language(lang, lang_list or [], language_aliases, 'wt-WT')
    lang_parts = lang_code.split('-')

    # country code goes first
    return lang_parts[1].lower() + '-' + lang_parts[0].lower()


def request(query, params):
    if params['time_range'] is not None and params['time_range'] not in time_range_dict:
        return params

    params['url'] = url
    params['method'] = 'POST'
    params['data']['b'] = ''
    params['data']['q'] = query
    params['data']['df'] = ''

    region_code = get_region_code(params['language'], supported_languages)
    if region_code:
        params['data']['kl'] = region_code
        params['cookies']['kl'] = region_code
    if params['time_range'] in time_range_dict:
        params['data']['df'] = time_range_dict[params['time_range']]

    return params


# get response from search-request
def response(resp):
    results = []

    doc = fromstring(resp.text)

    # parse results
    for i, r in enumerate(eval_xpath(doc, result_xpath)):
        if i >= 30:
            break
        try:
            res_url = eval_xpath(r, url_xpath)[-1]
        except:
            continue

        if not res_url:
            continue

        title = extract_text(eval_xpath(r, title_xpath))
        content = extract_text(eval_xpath(r, content_xpath))

        # append result
        results.append({'title': title,
                        'content': content,
                        'url': res_url})

    # parse correction
    for correction in eval_xpath(doc, correction_xpath):
        # append correction
        results.append({'correction': extract_text(correction)})

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

    return list(supported_languages)
