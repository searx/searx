# -*- coding: utf-8 -*-

"""
 Arch Linux Wiki

 @website      https://wiki.archlinux.org
 @provide-api  no (Mediawiki provides API, but Arch Wiki blocks access to it
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title
"""

from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode, urljoin

# engine dependent config
categories = ['it']
language_support = True
paging = True
base_url = 'https://wiki.archlinux.org'

# xpath queries
xpath_results = '//ul[@class="mw-search-results"]/li'
xpath_link = './/div[@class="mw-search-result-heading"]/a'


# cut 'en' from 'en_US', 'de' from 'de_CH', and so on
def locale_to_lang_code(locale):
    if locale.find('-') >= 0:
        locale = locale.split('-')[0]
    return locale


# wikis for some languages were moved off from the main site, we need to make
# requests to correct URLs to be able to get results in those languages
lang_urls = {
    'all': {
        'base': 'https://wiki.archlinux.org',
        'search': '/index.php?title=Special:Search&offset={offset}&{query}'
    },
    'de': {
        'base': 'https://wiki.archlinux.de',
        'search': '/index.php?title=Spezial:Suche&offset={offset}&{query}'
    },
    'fr': {
        'base': 'https://wiki.archlinux.fr',
        'search': '/index.php?title=Spécial:Recherche&offset={offset}&{query}'
    },
    'ja': {
        'base': 'https://wiki.archlinuxjp.org',
        'search': '/index.php?title=特別:検索&offset={offset}&{query}'
    },
    'ro': {
        'base': 'http://wiki.archlinux.ro',
        'search': '/index.php?title=Special:Căutare&offset={offset}&{query}'
    },
    'tr': {
        'base': 'http://archtr.org/wiki',
        'search': '/index.php?title=Özel:Ara&offset={offset}&{query}'
    }
}


# get base & search URLs for selected language
def get_lang_urls(language):
    if language in lang_urls:
        return lang_urls[language]
    return lang_urls['all']


# Language names to build search requests for
# those languages which are hosted on the main site.
main_langs = {
    'ar': 'العربية',
    'bg': 'Български',
    'cs': 'Česky',
    'da': 'Dansk',
    'el': 'Ελληνικά',
    'es': 'Español',
    'he': 'עברית',
    'hr': 'Hrvatski',
    'hu': 'Magyar',
    'it': 'Italiano',
    'ko': '한국어',
    'lt': 'Lietuviškai',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'pt': 'Português',
    'ru': 'Русский',
    'sl': 'Slovenský',
    'th': 'ไทย',
    'uk': 'Українська',
    'zh': '简体中文'
}
supported_languages = dict(lang_urls, **main_langs)


# do search-request
def request(query, params):
    # translate the locale (e.g. 'en_US') to language code ('en')
    language = locale_to_lang_code(params['language'])

    # if our language is hosted on the main site, we need to add its name
    # to the query in order to narrow the results to that language
    if language in main_langs:
        query += '(' + main_langs[language] + ')'

    # prepare the request parameters
    query = urlencode({'search': query})
    offset = (params['pageno'] - 1) * 20

    # get request URLs for our language of choice
    urls = get_lang_urls(language)
    search_url = urls['base'] + urls['search']

    params['url'] = search_url.format(query=query, offset=offset)

    return params


# get response from search-request
def response(resp):
    # get the base URL for the language in which request was made
    language = locale_to_lang_code(resp.search_params['language'])
    base_url = get_lang_urls(language)['base']

    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in dom.xpath(xpath_results):
        link = result.xpath(xpath_link)[0]
        href = urljoin(base_url, link.attrib.get('href'))
        title = extract_text(link)

        results.append({'url': href,
                        'title': title})

    return results
