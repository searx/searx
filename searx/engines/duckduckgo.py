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
from searx.engines.xpath import extract_text
from searx.languages import language_codes

# engine dependent config
categories = ['general']
paging = True
language_support = True
supported_languages = ["es-AR", "en-AU", "de-AT", "fr-BE", "nl-BE", "pt-BR", "bg-BG", "en-CA", "fr-CA", "ca-CT",
                       "es-CL", "zh-CN", "es-CO", "hr-HR", "cs-CZ", "da-DK", "et-EE", "fi-FI", "fr-FR", "de-DE",
                       "el-GR", "tzh-HK", "hu-HU", "en-IN", "id-ID", "en-ID", "en-IE", "he-IL", "it-IT", "jp-JP",
                       "kr-KR", "es-XL", "lv-LV", "lt-LT", "ms-MY", "en-MY", "es-MX", "nl-NL", "en-NZ", "no-NO",
                       "es-PE", "en-PH", "tl-PH", "pl-PL", "pt-PT", "ro-RO", "ru-RU", "ar-XA", "en-XA", "en-SG",
                       "sk-SK", "sl-SL", "en-ZA", "es-ES", "ca-ES", "sv-SE", "de-CH", "fr-CH", "it-CH", "tzh-TW",
                       "th-TH", "tr-TR", "uk-UA", "en-UK", "en-US", "es-US", "vi-VN"]
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
    elif params['language'] == 'es-419':
        locale = 'xl-es'
    else:
        locale = params['language'].split('-')
        if len(locale) == 2:
            # country code goes first
            locale = locale[1].lower() + '-' + locale[0].lower()
        else:
            # tries to get a country code from language
            locale = locale[0].lower()
            lang_codes = [x[0] for x in language_codes]
            for lc in lang_codes:
                lc = lc.split('-')
                if locale == lc[0] and len(lc) == 2:
                    locale = lc[1].lower() + '-' + lc[0].lower()
                    break

    if locale:
        params['url'] = url.format(
            query=urlencode({'q': query, 'kl': locale}), offset=offset)
    else:
        locale = params['language'].split('-')
        if len(locale) == 2:
            # country code goes first
            locale = locale[1].lower() + '-' + locale[0].lower()
        else:
            # tries to get a country code from language
            locale = locale[0].lower()
            lang_codes = [x[0] for x in language_codes]
            for lc in lang_codes:
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
