"""
 Gigablast (Web)

 @website     https://gigablast.com
 @provide-api yes (https://gigablast.com/api.html)

 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, content
"""

import random
from json import loads
from time import time
from lxml.html import fromstring
from searx.url_utils import urlencode

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
    '&rxieu={rxieu}'\
    '&rand={rxikd}'  # current unix timestamp

# specific xpath variables
results_xpath = '//response//result'
url_xpath = './/url'
title_xpath = './/title'
content_xpath = './/sum'

supported_languages_url = 'https://gigablast.com/search?&rxikd=1'


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

    # rxieu is some kind of hash from the search query, but accepts random atm
    search_path = search_string.format(query=urlencode({'q': query}),
                                       offset=offset,
                                       number_of_results=number_of_results,
                                       rxikd=int(time() * 1000),
                                       rxieu=random.randint(1000000000, 9999999999),
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


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = []
    dom = fromstring(resp.text)
    links = dom.xpath('//span[@id="menu2"]/a')
    for link in links:
        href = link.xpath('./@href')[0].split('lang%3A')
        if len(href) == 2:
            code = href[1].split('_')
            if len(code) == 2:
                code = code[0] + '-' + code[1].upper()
            else:
                code = code[0]
            supported_languages.append(code)

    return supported_languages
