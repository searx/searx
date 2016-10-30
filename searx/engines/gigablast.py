"""
 Gigablast (Web)

 @website     https://gigablast.com
 @provide-api yes (https://gigablast.com/api.html)

 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, content
"""

from json import loads
from random import randint
from time import time
from urllib import urlencode

# engine dependent config
categories = ['general']
paging = True
number_of_results = 10
language_support = True
safesearch = True

# search-url
base_url = 'https://gigablast.com/'
search_string = 'search?{query}'\
    '&n={number_of_results}'\
    '&c=main'\
    '&s={offset}'\
    '&format=json'\
    '&qh=0'\
    '&qlang={lang}'\
    '&ff={safesearch}'\
    '&rxikd={rxikd}'  # random number - 9 digits

# specific xpath variables
results_xpath = '//response//result'
url_xpath = './/url'
title_xpath = './/title'
content_xpath = './/sum'

supported_languages = ["en", "fr", "es", "ru", "tr", "ja", "zh-CN", "zh-TW", "ko", "de",
                       "nl", "it", "fi", "sv", "no", "pt", "vi", "ar", "he", "id", "el",
                       "th", "hi", "bn", "pl", "tl", "la", "eo", "ca", "bg", "tx", "sr",
                       "hu", "da", "lt", "cs", "gl", "ka", "gd", "go", "ro", "ga", "lv",
                       "hy", "is", "ag", "gv", "io", "fa", "te", "vv", "mg", "ku", "lb", "et"]


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * number_of_results

    if params['language'] == 'all':
        language = 'xx'
    else:
        language = params['language'].replace('-', '_').lower()
        if language.split('-')[0] != 'zh':
            language = language.split('-')[0]

    if params['safesearch'] >= 1:
        safesearch = 1
    else:
        safesearch = 0

    search_path = search_string.format(query=urlencode({'q': query}),
                                       offset=offset,
                                       number_of_results=number_of_results,
                                       rxikd=str(time())[:9],
                                       lang=language,
                                       safesearch=safesearch)

    params['url'] = base_url + search_path

    return params


# get response from search-request
def response(resp):
    results = []

    # parse results
    response_json = loads(resp.text)

    for result in response_json['results']:
        # append result
        results.append({'url': result['url'],
                        'title': result['title'],
                        'content': result['sum']})

    # return results
    return results
