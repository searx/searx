"""
 Yahoo (Web)

 @website     https://yandex.ru/
 @provide-api ?
 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from lxml import html
from searx import logger
from searx.url_utils import urlencode

logger = logger.getChild('yandex engine')

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
