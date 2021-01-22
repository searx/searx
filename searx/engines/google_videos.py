# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Google (Viedo)

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.  Not all parameters can be appied.

.. _admonition:: Content-Security-Policy (CSP)

   This engine needs to allow images from the `data URLs`_ (prefixed with the
   ``data:` scheme).::

     Header set Content-Security-Policy "img-src 'self' data: ;"

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions
.. _data URLs:
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs

"""

# pylint: disable=invalid-name, missing-function-docstring

import re
from urllib.parse import urlencode, urlparse
from lxml import html

from searx import logger
from searx.exceptions import SearxEngineCaptchaException
from searx.utils import (
    eval_xpath,
    eval_xpath_list,
    extract_text,
)

from searx.engines.google import (
    get_lang_country,
    google_domains,
    time_range_dict,
    filter_mapping,
    results_xpath,
    g_section_with_header,
    title_xpath,
    href_xpath,
    content_xpath,
    suggestion_xpath,
    spelling_suggestion_xpath
)

# pylint: disable=unused-import
from searx.engines.google import (
    supported_languages_url
    ,  _fetch_supported_languages
)
# pylint: enable=unused-import

# about
about = {
    "website": 'https://www.google.com',
    "wikidata_id": 'Q219885',
    "official_api_documentation": 'https://developers.google.com/custom-search/',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
    "template": 'video.html',
    "parse": ('url', 'title', 'content', 'thumbnail')
}

logger = logger.getChild('google video')

# engine dependent config

categories = ['videos']
paging = False
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = True

RE_CACHE = {}

def _re(regexpr):
    """returns compiled regular expression"""
    RE_CACHE[regexpr] = RE_CACHE.get(regexpr, re.compile(regexpr))
    return RE_CACHE[regexpr]

def scrap_out_thumbs(dom):
    """Scrap out thumbnail data from <script> tags.
    """
    ret_val = dict()
    thumb_name = 'vidthumb'

    for script in eval_xpath(dom, '//script[contains(., "_setImagesSrc")]'):
        _script = script.text

        # var s='data:image/jpeg;base64, ...'
        _imgdata = _re("s='([^']*)").findall( _script)
        if not _imgdata:
            continue

        # var ii=['vidthumb4','vidthumb7']
        for _vidthumb in _re(r"(%s\d+)" % thumb_name).findall(_script):
            # At least the equal sign in the URL needs to be decoded
            ret_val[_vidthumb] = _imgdata[0].replace(r"\x3d", "=")

    # {google.ldidly=-1;google.ldi={"vidthumb8":"https://...
    for script in eval_xpath(dom, '//script[contains(., "google.ldi={")]'):
        _script = script.text
        for key_val in _re(r'"%s\d+\":\"[^\"]*"' % thumb_name).findall( _script) :
            match = _re(r'"(%s\d+)":"(.*)"' % thumb_name).search(key_val)
            if match:
                # At least the equal sign in the URL needs to be decoded
                ret_val[match.group(1)] = match.group(2).replace(r"\u003d", "=")

    logger.debug("found %s imgdata for: %s", thumb_name, ret_val.keys())
    return ret_val


def request(query, params):
    """Google-Video search request"""

    language, country, lang_country = get_lang_country(
        # pylint: disable=undefined-variable
        params, supported_languages, language_aliases
    )
    subdomain = 'www.' + google_domains.get(country.upper(), 'google.com')

    query_url = 'https://'+ subdomain + '/search' + "?" + urlencode({
        'q':   query,
        'tbm': "vid",
        'hl':  lang_country,
        'lr': "lang_" + language,
        'ie': "utf8",
        'oe': "utf8",
    })

    if params['time_range'] in time_range_dict:
        query_url += '&' + urlencode({'tbs': 'qdr:' + time_range_dict[params['time_range']]})
    if params['safesearch']:
        query_url += '&' + urlencode({'safe': filter_mapping[params['safesearch']]})

    params['url'] = query_url
    logger.debug("query_url --> %s", query_url)

    # en-US,en;q=0.8,en;q=0.5
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
        raise SearxEngineCaptchaException()

    if resp_url.path.startswith('/sorry'):
        raise SearxEngineCaptchaException()

    # which subdomain ?
    # subdomain = resp.search_params.get('google_subdomain')

    # convert the text to dom
    dom = html.fromstring(resp.text)
    vidthumb_imgdata = scrap_out_thumbs(dom)

    # parse results
    for result in eval_xpath_list(dom, results_xpath):

        # google *sections*
        if extract_text(eval_xpath(result, g_section_with_header)):
            logger.debug("ingoring <g-section-with-header>")
            continue

        title = extract_text(eval_xpath(result, title_xpath)[0])
        url = eval_xpath(result, href_xpath)[0]
        c_node = eval_xpath(result, content_xpath)[0]

        # <img id="vidthumb1" ...>
        img_id = eval_xpath(c_node, './div[1]//a/g-img/img/@id')
        if not img_id:
            continue
        img_id = img_id[0]
        img_src = vidthumb_imgdata.get(img_id, None)
        if not img_src:
            logger.error("no vidthumb imgdata for: %s" % img_id)
            img_src = eval_xpath(c_node, './div[1]//a/g-img/img/@src')[0]

        duration = extract_text(eval_xpath(c_node, './div[1]//a/span'))
        content = extract_text(eval_xpath(c_node, './div[2]/span'))
        pub_info = extract_text(eval_xpath(c_node, './div[2]/div'))

        if len(duration) > 3:
            content = duration + " - " + content
        if pub_info:
            content = content + " (%s)" % pub_info

        results.append({
            'url':      url,
            'title':    title,
            'content':  content,
            'thumbnail':  img_src,
            'template': 'videos.html',
            })

    # parse suggestion
    for suggestion in eval_xpath(dom, suggestion_xpath):
        # append suggestion
        results.append({'suggestion': extract_text(suggestion)})

    for correction in eval_xpath(dom, spelling_suggestion_xpath):
        results.append({'correction': extract_text(correction)})

    return results
