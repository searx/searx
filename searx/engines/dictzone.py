"""
 Dictzone

 @website     https://dictzone.com/
 @provide-api no
 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

import re
from lxml import html
from searx.utils import is_valid_lang, eval_xpath
from searx.url_utils import urljoin

categories = ['general']
url = u'https://dictzone.com/{from_lang}-{to_lang}-dictionary/{query}'
weight = 100

parser_re = re.compile(b'.*?([a-z]+)-([a-z]+) ([^ ]+)$', re.I)
results_xpath = './/table[@id="r"]/tr'


def is_accepted(query, params):
    m = parser_re.match(query)
    if not m:
        return False

    params['parsed_regex'] = m
    from_lang, to_lang, query = m.groups()

    from_lang = is_valid_lang(from_lang)
    to_lang = is_valid_lang(to_lang)

    if not from_lang or not to_lang:
        return False

    params['from_lang'] = from_lang
    params['to_lang'] = to_lang
    params['query'] = query

    return True


def request(query, params):
    params['url'] = url.format(from_lang=params['from_lang'][2],
                               to_lang=params['to_lang'][2],
                               query=params['query'].decode('utf-8'))

    return params


def response(resp):
    results = []

    if resp.status_code != 200:
        return results

    dom = html.fromstring(resp.text)

    for k, result in enumerate(eval_xpath(dom, results_xpath)[1:]):
        try:
            from_result, to_results_raw = eval_xpath(result, './td')
        except:
            continue

        to_results = []
        for to_result in eval_xpath(to_results_raw, './p/a'):
            t = to_result.text_content()
            if t.strip():
                to_results.append(to_result.text_content())

        results.append({
            'url': urljoin(resp.url, '?%d' % k),
            'title': '[{0}-{1}] {2}'.format(
                resp.search_params['from_lang'][1],
                resp.search_params['to_lang'][1],
                from_result.text_content()),
        })

    return results
