# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google (Scholar)

:website:     https://scholar.google.com
:provide-api: yes (https://developers.google.com/custom-search/)
:using-api:   not the offical, since it needs registration to another service
:results:     HTML
:stable:      no
:parse:       url, title, content

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.  Not all parameters can be appied.

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions

"""

# pylint: disable=invalid-name, missing-function-docstring

from datetime import datetime
from lxml import html
from flask_babel import gettext
from searx import logger
from searx.url_utils import urlencode, urlparse
from searx.utils import eval_xpath
from searx.engines.xpath import extract_text

# pylint: disable=unused-import
from searx.engines.google import (
    supported_languages_url
    ,  _fetch_supported_languages
)
# pylint: enable=unused-import

from searx.engines.google import (
    get_lang_country
    , google_domains
    , filter_mapping
    , time_range_dict
    , extract_text_from_dom
)

suggestion_xpath = '//div[contains(@class, "gs_qsuggest_wrap")]//li//a'
spelling_suggestion_xpath = '//div[@class="gs_r gs_pda"]/a'
results_xpath = '//div[@class="gs_ri"]'
title_xpath = './h3[1]//a'
href_xpath = './h3[1]//a/@href'
content_xpath = './div[@class="gs_rs"]'
pub_info_xpath = './div[@class="gs_a"]'
pub_type_xpath = './/span[@class="gs_ct1"]'

logger = logger.getChild('google scholar')

# engine dependent config

categories = ['science']
paging = True
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = True

def time_range_url(params):
    """Returns a URL query component for a google-Scholar time range based on
    ``params['time_range']``.  Google-Scholar does only support ranges in years.
    To have any effect, all the Searx ranges (*day*, *week*, *month*, *year*)
    are mapped to *year*.  If no range is set, an empty string is returned.
    Example::

        &as_ylo=2019
    """
    # as_ylo=2016&as_yhi=2019
    ret_val = ''
    if params['time_range'] in time_range_dict:
        ret_val= urlencode({'as_ylo': datetime.now().year -1 })
    return '&' + ret_val


def request(query, params):
    """Google-Scholar search request"""

    offset = (params['pageno'] - 1) * 10
    language, country, lang_country = get_lang_country(
        # pylint: disable=undefined-variable
        params, supported_languages, language_aliases
    )
    subdomain = 'scholar.' + google_domains.get(country.upper(), 'google.com')

    query_url = 'https://'+ subdomain + '/scholar' + "?" + urlencode({
        'q':   query,
        'hl':  lang_country,
        'lr': "lang_" + language,
        'ie': "utf8",
        'oe':  "utf8",
        'start' : offset,
    })

    query_url += time_range_url(params)

    if params['safesearch']:
        query_url += '&' + urlencode({'safe': filter_mapping[params['safesearch']]})

    params['url'] = query_url
    logger.debug("query_url --> %s", query_url)

    params['headers']['Accept-Language'] = (
        "%s,%s;q=0.8,%s;q=0.5" % (lang_country, language, language))
    logger.debug(
        "HTTP Accept-Language --> %s", params['headers']['Accept-Language'])
    params['headers']['Accept'] = (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        )
    #params['google_subdomain'] = subdomain
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

    # which subdomain ?
    # subdomain = resp.search_params.get('google_subdomain')

    # convert the text to dom
    dom = html.fromstring(resp.text)

    # parse results
    for result in eval_xpath(dom, results_xpath):
        try:
            url = eval_xpath(result, href_xpath)
            if not url:
                continue

            url = url[0]
            title = extract_text(eval_xpath(result, title_xpath))
            content = extract_text_from_dom(result, content_xpath) or ''

            pub_info = extract_text_from_dom(result, pub_info_xpath)
            if pub_info:
                content += "[%s]" % pub_info

            pub_type = extract_text_from_dom(result, pub_type_xpath)
            if pub_type:
                title = pub_type + " " + title

            results.append({
                'url':      url,
                'title':    title,
                'content':  content,
                })

        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            continue

    # parse suggestion
    for suggestion in eval_xpath(dom, suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    for correction in eval_xpath(dom, spelling_suggestion_xpath):
        results.append({'correction': extract_text(correction)})

    return results
