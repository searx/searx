
"""Onesearch
"""

from lxml.html import fromstring

import re

from searx.utils import (
    eval_xpath,
    extract_text,
)

from urllib.parse import unquote

# about
about = {
    "website": 'https://www.onesearch.com/',
    "wikidata_id": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['general']
paging = True

# search-url
URL = 'https://www.onesearch.com/yhs/search;?p=%s&b=%d'


def request(query, params):
    starting_from = (params['pageno'] * 10) - 9
    params['url'] = URL % (query, starting_from)
    return params


# get response from search-request
def response(resp):

    results = []
    doc = fromstring(resp.text)

    titles_tags = eval_xpath(doc, '//div[contains(@class, "algo")]//h3[contains(@class, "title")]')
    contents = eval_xpath(doc, '//div[contains(@class, "algo")]/div[contains(@class, "compText")]/p')
    onesearch_urls = eval_xpath(doc, '//div[contains(@class, "algo")]//h3[contains(@class, "title")]/a/@href')

    for title_tag, content, onesearch_url in zip(titles_tags, contents, onesearch_urls):
        matches = re.search(r'RU=(.*?)\/', onesearch_url)
        results.append({
            'title': title_tag.text_content(),
            'content': extract_text(content),
            'url': unquote(matches.group(1)),
        })

    return results
