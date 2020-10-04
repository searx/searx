"""
 Duden
 @website     https://www.duden.de
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from lxml import html, etree
import re
from urllib.parse import quote, urljoin
from searx.utils import extract_text, eval_xpath
from searx import logger

categories = ['general']
paging = True
language_support = False

# search-url
base_url = 'https://www.duden.de/'
search_url = base_url + 'suchen/dudenonline/{query}?search_api_fulltext=&page={offset}'


def request(query, params):
    '''pre-request callback
    params<dict>:
      method  : POST/GET
      headers : {}
      data    : {} # if method == POST
      url     : ''
      category: 'search category'
      pageno  : 1 # number of the requested page
    '''

    offset = (params['pageno'] - 1)
    if offset == 0:
        search_url_fmt = base_url + 'suchen/dudenonline/{query}'
        params['url'] = search_url_fmt.format(query=quote(query))
    else:
        params['url'] = search_url.format(offset=offset, query=quote(query))
    return params


def response(resp):
    '''post-response callback
    resp: requests response object
    '''
    results = []

    dom = html.fromstring(resp.text)

    try:
        number_of_results_string =\
            re.sub('[^0-9]', '',
                   eval_xpath(dom, '//a[@class="active" and contains(@href,"/suchen/dudenonline")]/span/text()')[0])

        results.append({'number_of_results': int(number_of_results_string)})

    except:
        logger.debug("Couldn't read number of results.")
        pass

    for result in eval_xpath(dom, '//section[not(contains(@class, "essay"))]'):
        try:
            url = eval_xpath(result, './/h2/a')[0].get('href')
            url = urljoin(base_url, url)
            title = eval_xpath(result, 'string(.//h2/a)').strip()
            content = extract_text(eval_xpath(result, './/p'))
            # append result
            results.append({'url': url,
                            'title': title,
                            'content': content})
        except:
            logger.debug('result parse error in:\n%s', etree.tostring(result, pretty_print=True))
            continue

    return results
