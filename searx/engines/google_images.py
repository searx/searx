# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google (Images)

:website:     https://images.google.com (redirected to subdomain www.)
:provide-api: yes (https://developers.google.com/custom-search/)
:using-api:   not the offical, since it needs registration to another service
:results:     plain text (utf-8)
:stable:      yes
:template:    images.html
:parse:       url, title, content, source, img_format, thumbnail_src, img_src

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.

.. _admonition:: Content-Security-Policy (CSP)

   This engine needs to allow images from the `data URLs`_ (prefixed with the
   ``data:` scheme).::

     Header set Content-Security-Policy "img-src 'self' data: ;"

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions

"""

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
    , time_range_dict
    , filter_mapping
)

logger = logger.getChild('google images')

# engine dependent config

categories = ['images']
paging = False
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = False

# google results are grouped into <div class="g" ../>
results_xpath = '//div[@class="islrc"]       /div[contains(@class, "isv-r")]'

def scrap_out_thumbs(dom):
    """Scrap out thumbnail data from <script> tags.
    """
    ret_val = dict()
    for script in eval_xpath(dom, '//script[contains(., "_setImgSrc(")]'):
        _script = script.text
        # _setImgSrc('0','data:image\/jpeg;base64,\/9j\/4AAQSkZJR ....');
        _thumb_no, _img_data = _script[len("_setImgSrc("):-2].split(",",1)
        _thumb_no = _thumb_no.replace("'","")
        _img_data = _img_data.replace("'","")
        _img_data = _img_data.replace(r"\/", r"/")
        ret_val[_thumb_no] = _img_data[0].replace(r"\x3d", "=")
    return ret_val

def request(query, params):
    """Google-Video search request"""

    language, country = get_lang_country(
        # pylint: disable=undefined-variable
        params, supported_languages, language_aliases
    )
    subdomain = 'www.' + google_domains.get(country.upper(), 'google.com')

    query_url = 'https://'+ subdomain + '/search' + "?" + urlencode({
        'q':   query,
        'tbm': "isch",
        'hl':  language + "-" + country,
        'lr': "lang_" + language,
        'ie': "utf8",
        'oe': "utf8",
        'num': 30,
    })

    if params['time_range'] in time_range_dict:
        query_url += '&' + urlencode({'tbs': 'qdr:' + time_range_dict[params['time_range']]})
    if params['safesearch']:
        query_url += '&' + urlencode({'safe': filter_mapping[params['safesearch']]})

    params['url'] = query_url
    logger.debug("query_url --> %s", query_url)

    params['headers']['Accept-Language'] = (
        "%s-%s,%s;q=0.8,%s;q=0.5" % (language, country, language, language))
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
    img_bas64_map = scrap_out_thumbs(dom)

    # parse results
    #
    # root element::
    #     <div id="islmp" ..>
    # result div per image::
    #     <div jsmodel="tTXmib"> / <div jsaction="..."
    # first link per image-div contains a <img> with the data-iid for bas64 encoded image data::
    #      <img class="rg_i Q4LuWd" data-iid="0"
    # second link per image-div is the target link::
    #      <a class="VFACy kGQAp" href="https://en.wikipedia.org/wiki/The_Sacrament_of_the_Last_Supper">
    # the second link also contains two div tags with the *description* and *publisher*::
    #      <div class="WGvvNb">The Sacrament of the Last Supper ...</div>
    #      <div class="fxgdke">en.wikipedia.org</div>

    root = dom.xpath('//div[@id="islmp"]')
    if not root:
        logger.error("did not find root element id='islmp'")
        return results

    for img_node in root[0].xpath('.//img[contains(@class, "rg_i")]'):

        try:
            img_alt = img_node.xpath('@alt')[0]

            img_base64_id = img_node.xpath('@data-iid')
            if img_base64_id:
                img_base64_id = img_base64_id[0]
                thumbnail_src = img_bas64_map[img_base64_id]
            else:
                thumbnail_src = img_node.xpath('@src')
                if not thumbnail_src:
                    thumbnail_src = img_node.xpath('@data-src')
                if thumbnail_src:
                    thumbnail_src = thumbnail_src[0]
                else:
                    thumbnail_src = ''

            link_node = img_node.xpath('../../../a[2]')[0]
            url = link_node.xpath('@href')[0]

            pub_nodes = link_node.xpath('./div/div')
            pub_descr = img_alt
            pub_source = ''
            if pub_nodes:
                pub_descr = extract_text(pub_nodes[0])
                pub_source = extract_text(pub_nodes[1])

            results.append({
                'url': url,
                'title': img_alt,
                'content': pub_descr,
                'source': pub_source,
                # 'img_format': img_format,
                'thumbnail_src': thumbnail_src,
                'template': 'images.html'
            })
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            #from lxml import etree
            #logger.debug(etree.tostring(img_node, pretty_print=True))
            #import pdb
            #pdb.set_trace()
            continue

    return results
