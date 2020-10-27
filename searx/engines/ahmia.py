"""
 Ahmia (Onions)

 @website      http://msydqstlz2kzerdg.onion
 @provides-api no

 @using-api    no
 @results      HTML
 @stable       no
 @parse        url, title, content
"""

from urllib.parse import urlencode, urlparse, parse_qs
from lxml.html import fromstring
from searx.engines.xpath import extract_url, extract_text

# engine config
categories = ['onions']
paging = True
page_size = 10

# search url
search_url = 'http://msydqstlz2kzerdg.onion/search/?{query}'
time_range_support = True
time_range_dict = {'day': 1,
                   'week': 7,
                   'month': 30}

# xpaths
results_xpath = '//li[@class="result"]'
url_xpath = './h4/a/@href'
title_xpath = './h4/a[1]'
content_xpath = './/p[1]'
correction_xpath = '//*[@id="didYouMean"]//a'
number_of_results_xpath = '//*[@id="totalResults"]'


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    if params['time_range'] in time_range_dict:
        params['url'] += '&' + urlencode({'d': time_range_dict[params['time_range']]})

    return params


def response(resp):
    results = []
    dom = fromstring(resp.text)

    # trim results so there's not way too many at once
    first_result_index = page_size * (resp.search_params.get('pageno', 1) - 1)
    all_results = dom.xpath(results_xpath)
    trimmed_results = all_results[first_result_index:first_result_index + page_size]

    # get results
    for result in trimmed_results:
        # remove ahmia url and extract the actual url for the result
        raw_url = extract_url(result.xpath(url_xpath), search_url)
        cleaned_url = parse_qs(urlparse(raw_url).query).get('redirect_url', [''])[0]

        title = extract_text(result.xpath(title_xpath))
        content = extract_text(result.xpath(content_xpath))

        results.append({'url': cleaned_url,
                        'title': title,
                        'content': content,
                        'is_onion': True})

    # get spelling corrections
    for correction in dom.xpath(correction_xpath):
        results.append({'correction': extract_text(correction)})

    # get number of results
    number_of_results = dom.xpath(number_of_results_xpath)
    if number_of_results:
        try:
            results.append({'number_of_results': int(extract_text(number_of_results))})
        except:
            pass

    return results
