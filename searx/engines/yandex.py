# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Yahoo (Web)
"""

from urllib.parse import urlencode, urlparse
from lxml import html
from searx import logger
from searx.exceptions import SearxEngineCaptchaException

logger = logger.getChild('yandex engine')

# about
about = {
    "website": 'https://yandex.ru/',
    "wikidata_id": 'Q5281',
    "official_api_documentation": "?",
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general']
paging = True
language_support = True  # TODO

default_tld = 'com'
language_map = {'ru': 'ru',
                'ua': 'ua',
                'be': 'by',
                'kk': 'kz',
                'tr': 'com.tr'}

# search-url
base_url = 'https://yandex.{tld}/'
search_url = 'search/?{query}&p={page}'

results_xpath = '//li[@class="serp-item"]'
url_xpath = './/h2/a/@href'
title_xpath = './/h2/a//text()'
content_xpath = './/div[@class="text-container typo typo_text_m typo_line_m organic__text"]//text()'


def request(query, params):
    lang = params['language'].split('-')[0]
    host = base_url.format(tld=language_map.get(lang) or default_tld)
    params['url'] = host + search_url.format(page=params['pageno'] - 1,
                                             query=urlencode({'text': query}))
    return params


# get response from search-request
def response(resp):
    resp_url = urlparse(resp.url)
    if resp_url.path.startswith('/showcaptcha'):
        raise SearxEngineCaptchaException()

    dom = html.fromstring(resp.text)
    results = []

    for result in dom.xpath(results_xpath):
        try:
            res = {'url': result.xpath(url_xpath)[0],
                   'title': ''.join(result.xpath(title_xpath)),
                   'content': ''.join(result.xpath(content_xpath))}
        except:
            logger.exception('yandex parse crash')
            continue

        results.append(res)

    return results
