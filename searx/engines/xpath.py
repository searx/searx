# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint
# pylint: disable=missing-function-docstring
"""The XPath engine is a *generic* engine with which it is possible to configure
engines in the settings.

Here is a simple example of a XPath engine configured in the
:ref:`settings engine` section, further read :ref:`engines-dev`.

.. code:: yaml

  - name : bitbucket
    engine : xpath
    paging : True
    search_url : https://bitbucket.org/repo/all/{pageno}?name={query}
    url_xpath : //article[@class="repo-summary"]//a[@class="repo-link"]/@href
    title_xpath : //article[@class="repo-summary"]//a[@class="repo-link"]
    content_xpath : //article[@class="repo-summary"]/p

"""

from urllib.parse import urlencode

from lxml import html
from searx.utils import extract_text, extract_url, eval_xpath, eval_xpath_list
from searx import logger

logger = logger.getChild('XPath engine')

search_url = None
"""
Search URL of the engine, replacements are:

``{query}``:
  Search terms from user.

``{pageno}``:
  Page number if engine supports pagging :py:obj:`paging`

"""

soft_max_redirects = 0
'''Maximum redirects, soft limit. Record an error but don't stop the engine'''

results_xpath = ''
'''XPath selector for the list of result items'''

url_xpath = None
'''XPath selector of result's ``url``.'''

content_xpath = None
'''XPath selector of result's ``content``.'''

title_xpath = None
'''XPath selector of result's ``title``.'''

thumbnail_xpath = False
'''XPath selector of result's ``img_src``.'''

suggestion_xpath = ''
'''XPath selector of result's ``suggestion``.'''

cached_xpath = ''
cached_url = ''

paging = False
'''Engine supports paging [True or False].'''

page_size = 1
'''Number of results on each page.  Only needed if the site requires not a page
number, but an offset.'''

first_page_num = 1
'''Number of the first page (usually 0 or 1).'''

def request(query, params):
    '''Build request parameters (see :ref:`engine request`).

    '''
    query = urlencode({'q': query})[2:]

    fargs = {'query': query}
    if paging and search_url.find('{pageno}') >= 0:
        fargs['pageno'] = (params['pageno'] - 1) * page_size + first_page_num

    params['url'] = search_url.format(**fargs)
    params['query'] = query
    params['soft_max_redirects'] = soft_max_redirects
    logger.debug("query_url --> %s", params['url'])

    return params

def response(resp):
    '''Scrap *results* from the response (see :ref:`engine results`).

    '''
    results = []
    dom = html.fromstring(resp.text)
    is_onion = 'onions' in categories  # pylint: disable=undefined-variable

    if results_xpath:
        for result in eval_xpath_list(dom, results_xpath):

            url = extract_url(eval_xpath_list(result, url_xpath, min_len=1), search_url)
            title = extract_text(eval_xpath_list(result, title_xpath, min_len=1))
            content = extract_text(eval_xpath_list(result, content_xpath, min_len=1))
            tmp_result = {'url': url, 'title': title, 'content': content}

            # add thumbnail if available
            if thumbnail_xpath:
                thumbnail_xpath_result = eval_xpath_list(result, thumbnail_xpath)
                if len(thumbnail_xpath_result) > 0:
                    tmp_result['img_src'] = extract_url(thumbnail_xpath_result, search_url)

            # add alternative cached url if available
            if cached_xpath:
                tmp_result['cached_url'] = (
                    cached_url
                    + extract_text(eval_xpath_list(result, cached_xpath, min_len=1))
                )

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
                results.append({
                    'url': url,
                    'title': title,
                    'content': content,
                    'cached_url': cached_url + cached, 'is_onion': is_onion
                })
        else:
            for url, title, content in zip(
                (extract_url(x, search_url) for
                 x in eval_xpath_list(dom, url_xpath)),
                map(extract_text, eval_xpath_list(dom, title_xpath)),
                map(extract_text, eval_xpath_list(dom, content_xpath))
            ):
                results.append({
                    'url': url,
                    'title': title,
                    'content': content,
                    'is_onion': is_onion
                })

    if suggestion_xpath:
        for suggestion in eval_xpath(dom, suggestion_xpath):
            results.append({'suggestion': extract_text(suggestion)})

    logger.debug("found %s results", len(results))
    return results
