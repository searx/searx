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
from searx.poolrequests import get
from searx.url_utils import urlencode
from searx.utils import eval_xpath

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
    '&langcountry={lang}'\
    '&ff={safesearch}'\
    '&rand={rxikd}'
# specific xpath variables
results_xpath = '//response//result'
url_xpath = './/url'
title_xpath = './/title'
content_xpath = './/sum'

extra_param = ''  # gigablast requires a random extra parameter
# which can be extracted from the source code of the search page


def parse_extra_param(text):
    global extra_param
    param_lines = [x for x in text.splitlines() if x.startswith('var url=') or x.startswith('url=url+')]
    extra_param = ''
    for l in param_lines:
        extra_param += l.split("'")[1]
    extra_param = extra_param.split('&')[-1]


def init(engine_settings=None):
    parse_extra_param(get('http://gigablast.com/search?c=main&qlangcountry=en-us&q=south&s=10').text)


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
                                       lang=language,
                                       rxikd=int(time() * 1000),
                                       safesearch=safesearch)

    params['url'] = base_url + search_path + '&' + extra_param

    return params


# get response from search-request
def response(resp):
    results = []

    # parse results
    try:
        response_json = loads(resp.text)
    except:
        parse_extra_param(resp.text)
        raise Exception('extra param expired, please reload')

    for result in response_json['results']:
        # append result
        results.append({'url': result['url'],
                        'title': result['title'],
                        'content': result['sum']})

    # return results
    return results
