# SPDX-License-Identifier: AGPL-3.0-or-later
"""Google (Images)

:website:     https://images.google.com (redirected to subdomain www.)
:provide-api: yes (https://developers.google.com/custom-search/)
:using-api:   not the offical, since it needs registration to another service
:results:     HTML
:stable:      no
:template:    images.html
:parse:       url, title, content, source, thumbnail_src, img_src

For detailed description of the *REST-full* API see: `Query Parameter
Definitions`_.

.. _admonition:: Content-Security-Policy (CSP)

   This engine needs to allow images from the `data URLs`_ (prefixed with the
   ``data:` scheme).::

     Header set Content-Security-Policy "img-src 'self' data: ;"

.. _Query Parameter Definitions:
   https://developers.google.com/custom-search/docs/xml_results#WebSearch_Query_Parameter_Definitions

"""

from urllib.parse import urlencode, urlparse, unquote
from lxml import html
from searx import logger
from searx.exceptions import SearxEngineCaptchaException
from searx.utils import extract_text, eval_xpath
from searx.engines.google import _fetch_supported_languages, supported_languages_url  # NOQA # pylint: disable=unused-import

from searx.engines.google import (
    get_lang_country,
    google_domains,
    time_range_dict,
)

logger = logger.getChild('google images')

# engine dependent config

categories = ['images']
paging = False
language_support = True
use_locale_domain = True
time_range_support = True
safesearch = True

filter_mapping = {
    0: 'images',
    1: 'active',
    2: 'active'
}


def scrap_out_thumbs(dom):
    """Scrap out thumbnail data from <script> tags.
    """
    ret_val = dict()
    for script in eval_xpath(dom, '//script[contains(., "_setImgSrc(")]'):
        _script = script.text
        # _setImgSrc('0','data:image\/jpeg;base64,\/9j\/4AAQSkZJR ....');
        _thumb_no, _img_data = _script[len("_setImgSrc("):-2].split(",", 1)
        _thumb_no = _thumb_no.replace("'", "")
        _img_data = _img_data.replace("'", "")
        _img_data = _img_data.replace(r"\/", r"/")
        ret_val[_thumb_no] = _img_data.replace(r"\x3d", "=")
    return ret_val


def scrap_img_by_id(script, data_id):
    """Get full image URL by data-id in parent element
    """
    img_url = ''
    _script = script.split('\n')
    for i, line in enumerate(_script):
        if 'gstatic.com/images' in line and data_id in line:
            url_line = _script[i + 1]
            img_url = url_line.split('"')[1]
            img_url = unquote(img_url.replace(r'\u00', r'%'))
    return img_url


def request(query, params):
    """Google-Video search request"""

    language, country, lang_country = get_lang_country(
        # pylint: disable=undefined-variable
        params, supported_languages, language_aliases
    )
    subdomain = 'www.' + google_domains.get(country.upper(), 'google.com')

    query_url = 'https://' + subdomain + '/search' + "?" + urlencode({
        'q': query,
        'tbm': "isch",
        'hl': lang_country,
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
        "%s,%s;q=0.8,%s;q=0.5" % (lang_country, language, language))
    logger.debug(
        "HTTP Accept-Language --> %s", params['headers']['Accept-Language'])
    params['headers']['Accept'] = (
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    )
    # params['google_subdomain'] = subdomain
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
    img_bas64_map = scrap_out_thumbs(dom)
    img_src_script = eval_xpath(dom, '//script[contains(., "AF_initDataCallback({key: ")]')[1].text

    # parse results
    #
    # root element::
    #     <div id="islmp" ..>
    # result div per image::
    #     <div jsmodel="tTXmib"> / <div jsaction="..." data-id="..."
    #     The data-id matches to a item in a json-data structure in::
    #         <script nonce="I+vqelcy/01CKiBJi5Z1Ow">AF_initDataCallback({key: 'ds:1', ... data:function(){return [ ...
    #     In this structure the link to the origin PNG, JPG or whatever is given
    # first link per image-div contains a <img> with the data-iid for bas64 encoded image data::
    #      <img class="rg_i Q4LuWd" data-iid="0"
    # second link per image-div is the target link::
    #      <a class="VFACy kGQAp" href="https://en.wikipedia.org/wiki/The_Sacrament_of_the_Last_Supper">
    # the second link also contains two div tags with the *description* and *publisher*::
    #      <div class="WGvvNb">The Sacrament of the Last Supper ...</div>
    #      <div class="fxgdke">en.wikipedia.org</div>

    root = eval_xpath(dom, '//div[@id="islmp"]')
    if not root:
        logger.error("did not find root element id='islmp'")
        return results

    root = root[0]
    for img_node in eval_xpath(root, './/img[contains(@class, "rg_i")]'):

        try:
            img_alt = eval_xpath(img_node, '@alt')[0]

            img_base64_id = eval_xpath(img_node, '@data-iid')
            if img_base64_id:
                img_base64_id = img_base64_id[0]
                thumbnail_src = img_bas64_map[img_base64_id]
            else:
                thumbnail_src = eval_xpath(img_node, '@src')
                if not thumbnail_src:
                    thumbnail_src = eval_xpath(img_node, '@data-src')
                if thumbnail_src:
                    thumbnail_src = thumbnail_src[0]
                else:
                    thumbnail_src = ''

            link_node = eval_xpath(img_node, '../../../a[2]')[0]
            url = eval_xpath(link_node, '@href')[0]

            pub_nodes = eval_xpath(link_node, './div/div')
            pub_descr = img_alt
            pub_source = ''
            if pub_nodes:
                pub_descr = extract_text(pub_nodes[0])
                pub_source = extract_text(pub_nodes[1])

            img_src_id = eval_xpath(img_node, '../../../@data-id')[0]
            src_url = scrap_img_by_id(img_src_script, img_src_id)
            if not src_url:
                src_url = thumbnail_src

            results.append({
                'url': url,
                'title': img_alt,
                'content': pub_descr,
                'source': pub_source,
                'img_src': src_url,
                # 'img_format': img_format,
                'thumbnail_src': thumbnail_src,
                'template': 'images.html'
            })
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e, exc_info=True)
            # from lxml import etree
            # logger.debug(etree.tostring(img_node, pretty_print=True))
            # import pdb
            # pdb.set_trace()
            continue

    return results
