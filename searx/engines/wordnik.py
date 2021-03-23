# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Wordnik (general)
"""

from lxml.html import fromstring
from searx.utils import extract_text
from searx.raise_for_httperror import raise_for_httperror

# about
about = {
    "website": 'https://www.wordnik.com',
    "wikidata_id": 'Q8034401',
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

categories = ['general']
paging = False

URL = 'https://www.wordnik.com'
SEARCH_URL = URL + '/words/{query}'


def request(query, params):
    params['url'] = SEARCH_URL.format(query=query)
    return params


def response(resp):
    if resp.status_code == 404:
        return []

    try:
        dom = fromstring(resp.text)
    except Exception:
        raise_for_httperror(resp)
        return[]

    results = []
    word_defs = []
    word_defs_ib = []
    urls = []
    lines = ""
    lines_ib = "<div>"

    word_xpath = '//*[@id="headword"]/text()'
    from_xpath = '//*[@id="define"]/div/h3[1]'
    definitions_xpath = '//*[@id="define"]/div/ul[1]'
    misspelling_xpath = '//*[@id="define"]/div/ul/li/xref'

    word = extract_text(dom.xpath(word_xpath))
    definition_from = extract_text(dom.xpath(from_xpath))
    definitions = dom.xpath(definitions_xpath)
    definition_extra_ib = ""

    if len(definitions) == 0:
        return []

    for definition in definitions:
        for i in range(len(definition)):
            part_of_speach_xpath = f"./li[{i+1}]/abbr"
            definition_extra_xpath = f"./li[{i+1}]/i"
            definition_text_xpath = f"./li[{i+1}]"

            part_of_speach = extract_text(definition.xpath(part_of_speach_xpath))
            definition_text = extract_text(definition.xpath(definition_text_xpath))
            definition_extra = extract_text(definition.xpath(definition_extra_xpath))

            if 'misspelling' in definition_text.lower():
                urls.append({
                    'title': extract_text(definition.xpath(misspelling_xpath)),
                    'url': f"{URL}/words/{extract_text(definition.xpath(misspelling_xpath))}"})

            if definition_extra is not None and len(definition_extra) > 0:
                drop = f"{part_of_speach} {definition_extra}"
                definition_extra_ib = f"<em>({definition_extra})</em>"
                definition_extra = f"({definition_extra})"
            else:
                drop = f"{part_of_speach}"

            definition_text = definition_text.replace(drop, '').strip()

            word_defs_ib.append([
                i + 1,
                f"<em><u>{part_of_speach}</u></em>",
                definition_extra_ib,
                f"{definition_text}<br><br>"])

            word_defs.append([
                i + 1,
                part_of_speach,
                definition_extra,
                definition_text])

    for word_def_ib in word_defs_ib:
        lines_ib += f"{word_def_ib[0]}. \
                &nbsp; {word_def_ib[1]} \
                {word_def_ib[2]} \
                &nbsp; :: &nbsp; {word_def_ib[3]}"

    for word_def in word_defs:
        lines += f"{word_def[0]}. \
                {word_def[1]} \
                {word_def[2]} \
                :: {word_def[3]} | "

    lines_ib += f"<small>{definition_from}</small></div>"

    urls.append({'title': word, 'url': f"{URL}/words/{word}"})

    results.append({
        'infobox': word,
        'content': lines_ib,
        'urls': urls})

    results.append({
        'title': word,
        'content': lines[:-2],
        'url': urls[0]['url']})

    return results
