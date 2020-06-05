# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google (News)

:website:     https://news.google.com
:provide-api: yes (https://developers.google.com/custom-search/)

:using-api:   not the offical, since it needs registration to another service
:results:     HTML
:stable:      no (HTML can change)
:parse:       url, title

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions

"""

# pylint: disable=invalid-name, missing-function-docstring

import re
from lxml import html
from flask_babel import gettext
from searx import logger
from searx.url_utils import urlencode, urlparse
from searx.utils import eval_xpath

# pylint: disable=unused-import
from searx.engines.google import (
    supported_languages_url
    ,  _fetch_supported_languages
)
# pylint: enable=unused-import

from searx.engines.google import (
    get_lang_country
    , google_domains
    , time_range_dict
    , filter_mapping
)

logger = logger.getChild('google news')

# engine dependent config

categories = ['news']
paging = True
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = True

def request(query, params):
    """Google-News search request"""

    offset = (params['pageno'] - 1) * 10
    language, country = get_lang_country(
        # pylint: disable=undefined-variable
        params, supported_languages, language_aliases
    )
    subdomain = 'news.' + google_domains.get(country.upper(), 'google.com')

    query_url = 'https://'+ subdomain + '/search' + "?" + urlencode({'q': query})
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

    for result in eval_xpath(dom, '//div[@class="xrnccd"]'):

        try:
            # The first <a> tag in the <article> contains the link to the
            # article The href attribute of the <a> is a google internal link,
            # we can't use.  The real link is hidden in the jslog attribute:
            #
            #   <a ...
            #      jslog="95014; 4:https://www.cnn.com/.../index.html; track:click"
            #      href="./articles/CAIiENu3nGS...?hl=en-US&amp;gl=US&amp;ceid=US%3Aen"
            #      ... />

            jslog = eval_xpath(result, './article/a/@jslog')[0]
            url = re.findall('http[^;]*', jslog)[0]

            # the first <h3> tag in the <article> contains the title of the link
            title = eval_xpath(result, './article/h3//text()')[0]

            results.append({
                'url':      url,
                'title':    title,
                #'content':  content
                })

        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            continue

    # return results
    return results
