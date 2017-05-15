"""
 Yahoo (Web)

 @website     https://search.yahoo.com/web
 @provide-api yes (https://developer.yahoo.com/boss/search/),
              $0.80/1000 queries

 @using-api   no (because pricing)
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content, suggestion
"""

from lxml import html
from searx.engines.xpath import extract_text, extract_url
from searx.url_utils import unquote, urlencode

# engine dependent config
categories = ['general']
paging = True
language_support = True
time_range_support = True

# search-url
base_url = 'https://search.yahoo.com/'
search_url = 'search?{query}&b={offset}&fl=1&vl=lang_{lang}'
search_url_with_time = 'search?{query}&b={offset}&fl=1&vl=lang_{lang}&age={age}&btf={btf}&fr2=time'

supported_languages_url = 'https://search.yahoo.com/web/advanced'

# specific xpath variables
results_xpath = "//div[contains(concat(' ', normalize-space(@class), ' '), ' Sr ')]"
url_xpath = './/h3/a/@href'
title_xpath = './/h3/a'
content_xpath = './/div[@class="compText aAbs"]'
suggestion_xpath = "//div[contains(concat(' ', normalize-space(@class), ' '), ' AlsoTry ')]//a"

time_range_dict = {'day': ['1d', 'd'],
                   'week': ['1w', 'w'],
                   'month': ['1m', 'm']}


# remove yahoo-specific tracking-url
def parse_url(url_string):
    endings = ['/RS', '/RK']
    endpositions = []
    start = url_string.find('http', url_string.find('/RU=') + 1)

    for ending in endings:
        endpos = url_string.rfind(ending)
        if endpos > -1:
            endpositions.append(endpos)

    if start == 0 or len(endpositions) == 0:
        return url_string
    else:
        end = min(endpositions)
        return unquote(url_string[start:end])


def _get_url(query, offset, language, time_range):
    if time_range in time_range_dict:
        return base_url + search_url_with_time.format(offset=offset,
                                                      query=urlencode({'p': query}),
                                                      lang=language,
                                                      age=time_range_dict[time_range][0],
                                                      btf=time_range_dict[time_range][1])
    return base_url + search_url.format(offset=offset,
                                        query=urlencode({'p': query}),
                                        lang=language)


def _get_language(params):
    if params['language'] == 'all':
        return 'en'
    elif params['language'][:2] == 'zh':
        if params['language'] == 'zh' or params['language'] == 'zh-CH':
            return 'szh'
        else:
            return 'tzh'
    else:
        return params['language'].split('-')[0]


# do search-request
def request(query, params):
    if params['time_range'] and params['time_range'] not in time_range_dict:
        return params

    offset = (params['pageno'] - 1) * 10 + 1
    language = _get_language(params)

    params['url'] = _get_url(query, offset, language, params['time_range'])

    # TODO required?
    params['cookies']['sB'] = 'fl=1&vl=lang_{lang}&sh=1&rw=new&v=1'\
        .format(lang=language)

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    try:
        results_num = int(dom.xpath('//div[@class="compPagination"]/span[last()]/text()')[0]
                          .split()[0].replace(',', ''))
        results.append({'number_of_results': results_num})
    except:
        pass

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
    suggestions = dom.xpath(suggestion_xpath)
    if not suggestions:
        return results

    # parse suggestion
    for suggestion in suggestions:
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = []
    dom = html.fromstring(resp.text)
    options = dom.xpath('//div[@id="yschlang"]/span/label/input')
    for option in options:
        code = option.xpath('./@value')[0][5:].replace('_', '-')
        supported_languages.append(code)

    return supported_languages
