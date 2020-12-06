"""
 Wikipedia (Web)

 @website     https://en.wikipedia.org/api/rest_v1/
 @provide-api yes

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, infobox
"""

from urllib.parse import quote
from json import loads
from lxml.html import fromstring
from searx.utils import match_language, searx_useragent
from searx.raise_for_httperror import raise_for_httperror

# search-url
search_url = 'https://{language}.wikipedia.org/api/rest_v1/page/summary/{title}'
supported_languages_url = 'https://meta.wikimedia.org/wiki/List_of_Wikipedias'


# set language in base_url
def url_lang(lang):
    lang_pre = lang.split('-')[0]
    if lang_pre == 'all' or lang_pre not in supported_languages and lang_pre not in language_aliases:
        return 'en'
    return match_language(lang, supported_languages, language_aliases).split('-')[0]


# do search-request
def request(query, params):
    if query.islower():
        query = query.title()

    params['url'] = search_url.format(title=quote(query),
                                      language=url_lang(params['language']))

    params['headers']['User-Agent'] = searx_useragent()
    params['raise_for_httperror'] = False
    params['soft_max_redirects'] = 2

    return params


# get response from search-request
def response(resp):
    if resp.status_code == 404:
        return []
    raise_for_httperror(resp)

    results = []
    api_result = loads(resp.text)

    # skip disambiguation pages
    if api_result.get('type') != 'standard':
        return []

    title = api_result['title']
    wikipedia_link = api_result['content_urls']['desktop']['page']

    results.append({'url': wikipedia_link, 'title': title})

    results.append({'infobox': title,
                    'id': wikipedia_link,
                    'content': api_result.get('extract', ''),
                    'img_src': api_result.get('thumbnail', {}).get('source'),
                    'urls': [{'title': 'Wikipedia', 'url': wikipedia_link}]})

    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = {}
    dom = fromstring(resp.text)
    tables = dom.xpath('//table[contains(@class,"sortable")]')
    for table in tables:
        # exclude header row
        trs = table.xpath('.//tr')[1:]
        for tr in trs:
            td = tr.xpath('./td')
            code = td[3].xpath('./a')[0].text
            name = td[2].xpath('./a')[0].text
            english_name = td[1].xpath('./a')[0].text
            articles = int(td[4].xpath('./a/b')[0].text.replace(',', ''))
            # exclude languages with too few articles
            if articles >= 100:
                supported_languages[code] = {"name": name, "english_name": english_name, "articles": articles}

    return supported_languages
