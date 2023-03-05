# SPDX-License-Identifier: AGPL-3.0-or-later

from lxml import html
from urllib.parse import urlencode
from searx.utils import extract_text, extract_url, eval_xpath, eval_xpath_list

search_url = None
lang_all = 'en'
url_xpath = None
content_xpath = None
title_xpath = None
thumbnail_xpath = False
paging = False
suggestion_xpath = ''
results_xpath = ''
cached_xpath = ''
cached_url = ''
soft_max_redirects = 0

cookies = {}
headers = {}
'''Some engines might offer different result based on cookies or headers.
Possible use-case: To set safesearch cookie or header to moderate.'''

paging = False
'''Engine supports paging [True or False].'''

page_size = 1
# number of the first page (usually 0 or 1)
first_page_num = 1


time_range_support = False
'''Engine supports search time range.'''

time_range_url = '&hours={time_range_val}'
'''Time range URL parameter in the in :py:obj:`search_url`.  If no time range is
requested by the user, the URL parameter is an empty string.  The
``{time_range_val}`` replacement is taken from the :py:obj:`time_range_map`.

.. code:: yaml

    time_range_url : '&days={time_range_val}'
'''

time_range_map = {
    'day': 24,
    'week': 24 * 7,
    'month': 24 * 30,
    'year': 24 * 365,
}
'''Maps time range value from user to ``{time_range_val}`` in
:py:obj:`time_range_url`.

.. code:: yaml

    time_range_map:
      day: 1
      week: 7
      month: 30
      year: 365
'''

safe_search_support = False
'''Engine supports safe-search.'''

safe_search_map = {
    0: '&filter=none',
    1: '&filter=moderate',
    2: '&filter=strict'
}
'''Maps safe-search value to ``{safe_search}`` in :py:obj:`search_url`.

.. code:: yaml

    safesearch: true
    safes_search_map:
      0: '&filter=none'
      1: '&filter=moderate'
      2: '&filter=strict'

'''


def request(query, params):
    query = urlencode({'q': query})[2:]

    fp = {'query': query}
    if paging and search_url.find('{pageno}') >= 0:
        fp['pageno'] = (params['pageno'] - 1) * page_size + first_page_num

    safe_search = ''
    if params['safesearch']:
        safe_search = safe_search_map[params['safesearch']]

    lang = lang_all
    if params['language'] != 'all':
        lang = params['language'][:2]

    time_range = ''
    if params.get('time_range'):
        time_range_val = time_range_map.get(params.get('time_range'))
        time_range = time_range_url.format(time_range_val=time_range_val)

    safe_search = ''
    if params['safesearch']:
        safe_search = safe_search_map[params['safesearch']]

    fargs = {
        'query': urlencode({'q': query})[2:],
        'lang': lang,
        'pageno': (params['pageno'] - 1) * page_size + first_page_num,
        'time_range': time_range,
        'safe_search': safe_search,
    }

    params['cookies'].update(cookies)
    params['headers'].update(headers)

    params['url'] = search_url.format(**fargs)
    params['soft_max_redirects'] = soft_max_redirects

    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)
    is_onion = True if 'onions' in categories else False  # pylint: disable=undefined-variable

    if results_xpath:
        for result in eval_xpath_list(dom, results_xpath):
            url = extract_url(eval_xpath_list(result, url_xpath, min_len=1), search_url)
            title = extract_text(eval_xpath_list(result, title_xpath, min_len=1))
            content = extract_text(eval_xpath_list(result, content_xpath))
            tmp_result = {'url': url, 'title': title, 'content': content}

            # add thumbnail if available
            if thumbnail_xpath:
                thumbnail_xpath_result = eval_xpath_list(result, thumbnail_xpath)
                if len(thumbnail_xpath_result) > 0:
                    tmp_result['img_src'] = extract_url(thumbnail_xpath_result, search_url)

            # add alternative cached url if available
            if cached_xpath:
                tmp_result['cached_url'] = cached_url\
                    + extract_text(eval_xpath_list(result, cached_xpath, min_len=1))

            if is_onion:
                tmp_result['is_onion'] = True

            results.append(tmp_result)
    else:
        if cached_xpath:
            for url, title, content, cached in zip(
                (extract_url(x, search_url) for
                 x in eval_xpath_list(dom, url_xpath)),
                map(extract_text, eval_xpath_list(dom, title_xpath)),
                map(extract_text, eval_xpath_list(dom, content_xpath)),
                map(extract_text, eval_xpath_list(dom, cached_xpath))
            ):
                results.append({'url': url, 'title': title, 'content': content,
                                'cached_url': cached_url + cached, 'is_onion': is_onion})
        else:
            for url, title, content in zip(
                (extract_url(x, search_url) for
                 x in eval_xpath_list(dom, url_xpath)),
                map(extract_text, eval_xpath_list(dom, title_xpath)),
                map(extract_text, eval_xpath_list(dom, content_xpath))
            ):
                results.append({'url': url, 'title': title, 'content': content, 'is_onion': is_onion})

    if not suggestion_xpath:
        return results
    for suggestion in eval_xpath(dom, suggestion_xpath):
        results.append({'suggestion': extract_text(suggestion)})
    return results
