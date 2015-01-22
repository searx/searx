## Yahoo (Web)
#
# @website     https://search.yahoo.com/web
# @provide-api yes (https://developer.yahoo.com/boss/search/),
#              $0.80/1000 queries
#
# @using-api   no (because pricing)
# @results     HTML (using search portal)
# @stable      no (HTML can change)
# @parse       url, title, content, suggestion

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urlencode
from urllib.parse import unquote
from lxml import html
from searx.engines.xpath import extract_text, extract_url

# engine dependent config
categories = ['general']
paging = True
language_support = True

# search-url
base_url = 'https://search.yahoo.com/'
search_url = 'search?{query}&b={offset}&fl=1&vl=lang_{lang}'

# specific xpath variables
results_xpath = '//div[@class="res"]'
url_xpath = './/h3/a/@href'
title_xpath = './/h3/a'
content_xpath = './/div[@class="abstr"]'
suggestion_xpath = '//div[@id="satat"]//a'


# remove yahoo-specific tracking-url
def parse_url(url_string):
    endings = ['/RS', '/RK']
    endpositions = []
    start = url_string.find('http', url_string.find('/RU=')+1)

    for ending in endings:
        endpos = url_string.rfind(ending)
        if endpos > -1:
            endpositions.append(endpos)

    if start == 0 or len(endpositions) == 0:
        return url_string
    else:
        end = min(endpositions)
        return unquote(url_string[start:end])


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10 + 1

    if params['language'] == 'all':
        language = 'en'
    else:
        language = params['language'].split('_')[0]

    params['url'] = base_url + search_url.format(offset=offset,
                                                 query=urlencode({'p': query}),
                                                 lang=language)

    # TODO required?
    params['cookies']['sB'] = 'fl=1&vl=lang_{lang}&sh=1&rw=new&v=1'\
        .format(lang=language)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(results_xpath):
        try:
            url = parse_url(extract_url(result.xpath(url_xpath), search_url))
            title = extract_text(result.xpath(title_xpath)[0])
        except:
            continue

        content = extract_text(result.xpath(content_xpath)[0])

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # if no suggestion found, return results
    if not suggestion_xpath:
        return results

    # parse suggestion
    for suggestion in dom.xpath(suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    # return results
    return results
