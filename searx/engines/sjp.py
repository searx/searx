# SPDX-License-Identifier: AGPL-3.0-or-later
"""Słownik Języka Polskiego (general)

"""

from lxml.html import fromstring
from searx import logger
from searx.utils import extract_text
from searx.raise_for_httperror import raise_for_httperror

logger = logger.getChild('sjp engine')

# about
about = {
    "website": 'https://sjp.pwn.pl',
    "wikidata_id": 'Q55117369',
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

categories = ['general']
paging = False

URL = 'https://sjp.pwn.pl'
SEARCH_URL = URL + '/szukaj/{query}.html'


def request(query, params):
    params['url'] = SEARCH_URL.format(query=query)
    logger.debug(f"query_url --> {params['url']}")
    return params


def response(resp):
    results = []

    raise_for_httperror(resp)
    dom = fromstring(resp.text)
    word = extract_text(dom.xpath('//*[@id="content"]/div/div[1]/div/div[1]/div[1]/div[2]/div/div/div[2]/div/div'))

    definitions = []
    for src in dom.xpath('//*[@id="content"]/div/div[1]/div/div[1]/div[1]/div[2]/div/div/div/div/div/div'):
        src_text = extract_text(src.xpath('./h1/span[@class="entry-head-title"]/text()')).strip()

        src_defs = []
        for def_item in src.xpath('./div/div[contains(@class, "ribbon-element")]'):
            if def_item.xpath('./div[@class="znacz"]'):
                sub_defs = []
                for def_sub_item in def_item.xpath('./div[@class="znacz"]'):
                    def_sub_text = extract_text(def_sub_item).lstrip('0123456789. ')
                    sub_defs.append(def_sub_text)
                src_defs.append((word, sub_defs))
            else:
                def_text = extract_text(def_item).strip()
                src_defs.append((def_text, ''))

        definitions.append((src_text, src_defs))

    if not definitions:
        return results

    infobox = ''
    for src in definitions:
        infobox += f"<div><small>{src[0]}</small>"
        infobox += "<ul>"
        for (def_text, sub_def) in src[1]:
            infobox += f"<li>{def_text}</li>"
            if sub_def:
                infobox += "<ol>"
                for sub_def_text in sub_def:
                    infobox += f"<li>{sub_def_text}</li>"
                infobox += "</ol>"
        infobox += "</ul></div>"

    results.append({
        'infobox': word,
        'content': infobox,
    })

    return results
