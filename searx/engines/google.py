# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google (Web)

@website     https://www.google.com
@provide-api yes (https://developers.google.com/custom-search/)

@using-api   no
@results     HTML
@stable      no (HTML can change)
@parse       url, title, content, number_of_results, answer, suggestion, correction

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions

"""

# pylint: disable=invalid-name, missing-function-docstring

from lxml import html
from flask_babel import gettext
from searx.engines.xpath import extract_text
from searx import logger
from searx.url_utils import urlencode, urlparse
from searx.utils import match_language, eval_xpath

logger = logger.getChild('google engine')

# engine dependent config
categories = ['general']
paging = True
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = True

supported_languages_url = 'https://www.google.com/preferences?#languages'

# based on https://en.wikipedia.org/wiki/List_of_Google_domains and tests
default_hostname = 'www.google.com'

country_to_hostname = {
    'BG': 'www.google.bg',      # Bulgaria
    'CZ': 'www.google.cz',      # Czech Republic
    'DE': 'www.google.de',      # Germany
    'DK': 'www.google.dk',      # Denmark
    'AT': 'www.google.at',      # Austria
    'CH': 'www.google.ch',      # Switzerland
    'GR': 'www.google.gr',      # Greece
    'AU': 'www.google.com.au',  # Australia
    'CA': 'www.google.ca',      # Canada
    'GB': 'www.google.co.uk',   # United Kingdom
    'ID': 'www.google.co.id',   # Indonesia
    'IE': 'www.google.ie',      # Ireland
    'IN': 'www.google.co.in',   # India
    'MY': 'www.google.com.my',  # Malaysia
    'NZ': 'www.google.co.nz',   # New Zealand
    'PH': 'www.google.com.ph',  # Philippines
    'SG': 'www.google.com.sg',  # Singapore
    # 'US': 'www.google.us',    # United States, redirect to .com
    'ZA': 'www.google.co.za',   # South Africa
    'AR': 'www.google.com.ar',  # Argentina
    'CL': 'www.google.cl',      # Chile
    'ES': 'www.google.es',      # Spain
    'MX': 'www.google.com.mx',  # Mexico
    'EE': 'www.google.ee',      # Estonia
    'FI': 'www.google.fi',      # Finland
    'BE': 'www.google.be',      # Belgium
    'FR': 'www.google.fr',      # France
    'IL': 'www.google.co.il',   # Israel
    'HR': 'www.google.hr',      # Croatia
    'HU': 'www.google.hu',      # Hungary
    'IT': 'www.google.it',      # Italy
    'JP': 'www.google.co.jp',   # Japan
    'KR': 'www.google.co.kr',   # South Korea
    'LT': 'www.google.lt',      # Lithuania
    'LV': 'www.google.lv',      # Latvia
    'NO': 'www.google.no',      # Norway
    'NL': 'www.google.nl',      # Netherlands
    'PL': 'www.google.pl',      # Poland
    'BR': 'www.google.com.br',  # Brazil
    'PT': 'www.google.pt',      # Portugal
    'RO': 'www.google.ro',      # Romania
    'RU': 'www.google.ru',      # Russia
    'SK': 'www.google.sk',      # Slovakia
    'SI': 'www.google.si',      # Slovenia
    'SE': 'www.google.se',      # Sweden
    'TH': 'www.google.co.th',   # Thailand
    'TR': 'www.google.com.tr',  # Turkey
    'UA': 'www.google.com.ua',  # Ukraine
    # 'CN': 'www.google.cn',    # China, only from China ?
    'HK': 'www.google.com.hk',  # Hong Kong
    'TW': 'www.google.com.tw'   # Taiwan
}

time_range_dict = {
    'day': 'd',
    'week': 'w',
    'month': 'm',
    'year': 'y'
}

# Filter results. 0: None, 1: Moderate, 2: Strict
filter_mapping = {
    0 : 'off',
    1 : 'medium',
    2 : 'high'
}

# specific xpath variables
# ------------------------

# google results are grouped into <div class="g" ../>
results_xpath = '//div[@class="g"]'

# google *sections* are no usual *results*, we ignore them
g_section_with_header='./g-section-with-header'

# the title is a h3 tag relative to the result group
title_xpath = './/h3[1]'

# in the result group there is <div class="r" ../> it's first child is a <a
# href=...> (on some results, the <a> is the first "descendant", not ""child")
href_xpath = './/div[@class="r"]//a/@href'

# in the result group there is <div class="s" ../> containing he *content*
content_xpath = './/div[@class="s"]'

# Suggestions are links placed in a *card-section*, we extract only the text
# from the links not the links itself.
suggestion_xpath = '//div[contains(@class, "card-section")]//a'

# Since google does *auto-correction* on the first query these are not really
# *spelling suggestions*, we use them anyway.
spelling_suggestion_xpath = '//div[@class="med"]/p/a'

def extract_text_from_dom(result, xpath):
    """returns extract_text on the first result selected by the xpath or None"""
    r = eval_xpath(result, xpath)
    if len(r) > 0:
        return extract_text(r[0])
    return None

def request(query, params):
    """Google search request"""
    offset = (params['pageno'] - 1) * 10

    language = params['language']
    if language == 'all':
        language = 'en-US'

    language_array = language.split('-')

    if len(language_array) == 2:
        country = language_array[1]
    else:
        country = language_array[0].upper()

    language = match_language(
        language,
        supported_languages, # pylint: disable=undefined-variable
        language_aliases     # pylint: disable=undefined-variable
    )

    google_hostname = default_hostname
    if use_locale_domain:
        google_hostname = country_to_hostname.get(country.upper(), default_hostname)

    # https://www.google.de/search?q=corona&hl=de-DE&lr=lang_de&start=0&tbs=qdr%3Ad&safe=medium

    query_url = 'https://'+ google_hostname + '/search' + "?" + urlencode({'q': query})
    query_url += '&' + urlencode({'hl': language + "-" + country})
    query_url += '&' + urlencode({'lr': "lang_" + language})
    query_url += '&' + urlencode({'ie': "utf8"})
    query_url += '&' + urlencode({'oe': "utf8"})
    query_url += '&' + urlencode({'start': offset})
    if params['time_range'] in time_range_dict:
        query_url += '&' + urlencode({'tbs': 'qdr:' + time_range_dict[params['time_range']]})
    if params['safesearch']:
        query_url += '&' + urlencode({'safe': filter_mapping[params['safesearch']]})

    params['url'] = query_url
    logger.debug("query_url --> %s", query_url)

    # en-US,en;q=0.8,en;q=0.5
    params['headers']['Accept-Language'] = (
        language + '-' + country + ',' + language + ';q=0.8,' + language + ';q=0.5'
        )
    logger.debug("HTTP header Accept-Language --> %s",
                 params['headers']['Accept-Language'])
    params['headers']['Accept'] = (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        )
    params['google_hostname'] = google_hostname

    return params

def response(resp):
    """Get response from google's search request"""
    results = []

    # detect google sorry
    resp_url = urlparse(resp.url)
    if resp_url.netloc == 'sorry.google.com' or resp_url.path == '/sorry/IndexRedirect':
        raise RuntimeWarning('sorry.google.com')

    if resp_url.path.startswith('/sorry'):
        raise RuntimeWarning(gettext('CAPTCHA required'))

    # which hostname ?
    # google_hostname = resp.search_params.get('google_hostname')

    # convert the text to dom
    dom = html.fromstring(resp.text)

    # results --> answer
    answer = eval_xpath(dom, '//div[contains(@class, "LGOjhe")]//text()')
    if answer:
        results.append({'answer': ' '.join(answer)})
    else:
        logger.debug("did not found 'answer'")

    # results --> number_of_results
    try:
        _txt = eval_xpath(dom, '//div[@id="result-stats"]//text()')[0]
        _txt = _txt.split()[1]
        _txt = _txt.replace(',', '').replace('.', '')
        number_of_results = int(_txt)
        results.append({'number_of_results': number_of_results})

    except Exception as e:  # pylint: disable=broad-except
        logger.debug("did not 'number_of_results'")
        logger.error(e, exc_info=True)

    # parse results
    for result in eval_xpath(dom, results_xpath):

        # google *sections*
        if extract_text(eval_xpath(result, g_section_with_header)):
            logger.debug("ingoring <g-section-with-header>")
            continue

        try:
            title = extract_text(eval_xpath(result, title_xpath)[0])
            url = eval_xpath(result, href_xpath)[0]
            content = extract_text_from_dom(result, content_xpath)
            results.append({
                'url':      url,
                'title':    title,
                'content':  content
                })
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            #from lxml import etree
            #logger.debug(etree.tostring(result, pretty_print=True))
            #import pdb
            #pdb.set_trace()
            continue

    # parse suggestion
    for suggestion in eval_xpath(dom, suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    for correction in eval_xpath(dom, spelling_suggestion_xpath):
        results.append({'correction': extract_text(correction)})

    # return results
    return results

# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = {}
    dom = html.fromstring(resp.text)

    radio_buttons = eval_xpath(dom, '//*[@id="langSec"]//input[@name="lang"]')

    for x in radio_buttons:
        name = x.get("data-name")
        code = x.get("value")
        supported_languages[code] = {"name": name}

    return supported_languages
