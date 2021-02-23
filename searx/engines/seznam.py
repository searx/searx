# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Seznam
"""

from urllib.parse import urlencode, urlparse
from lxml import html
from searx.poolrequests import get
from searx.exceptions import SearxEngineAccessDeniedException
from searx.utils import extract_text, eval_xpath_list, eval_xpath_getindex

# about
about = {
    "website": "https://www.seznam.cz/",
    "wikidata_id": "Q3490485",
    "official_api_documentation": "https://api.sklik.cz/",
    "use_official_api": False,
    "require_api_key": False,
    "results": "HTML",
}

base_url = 'https://search.seznam.cz/'


def request(query, params):
    response_index = get(base_url, headers=params['headers'], raise_for_httperror=True)
    dom = html.fromstring(response_index.text)

    url_params = {'q': query}
    for e in eval_xpath_list(dom, '//input[@type="hidden"]'):
        name = e.get('name')
        value = e.get('value')
        url_params[name] = value

    params['url'] = base_url + '?' + urlencode(url_params)
    params['cookies'] = response_index.cookies
    return params


def response(resp):
    resp_url = urlparse(resp.url)
    if resp_url.path.startswith('/verify'):
        raise SearxEngineAccessDeniedException()

    results = []

    dom = html.fromstring(resp.content.decode())
    for result_element in eval_xpath_list(dom, '//div[@id="searchpage-root"]//div[@data-dot="results"]/div'):
        dot_data = eval_xpath_getindex(result_element, './div/div[@data-dot-data]/@data-dot-data', 0, default=None)
        if dot_data is None:
            title_element = eval_xpath_getindex(result_element, './/h3/a', 0)
            results.append({
                'url': title_element.get('href'),
                'title': extract_text(title_element),
                'content': extract_text(eval_xpath_getindex(title_element, '../../div[2]', 0)),
            })
        elif dot_data == '{"reporter_name":"hint/related/relates"}':
            suggestions_element = eval_xpath_getindex(result_element,
                                                      './div/div[@data-dot="main-box"]', 0, default=None)
            if suggestions_element is not None:
                for suggestion in eval_xpath_list(suggestions_element, './/ul/li'):
                    results.append({'suggestion': extract_text(suggestion)})

    return results
