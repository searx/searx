#!/usr/bin/env python

"""
 torznab (torrent search)

 @website     https://github.com/Jackett/Jackett
 @provide-api yes (but you have to be hosted)

 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, publishedDate, content, magentlink, seed, leech, filesize
 Although torznab is just the format, the most simple way to set it up is via Jackett.
 More info on torznab: https://torznab.github.io/spec-1.3-draft/torznab/Specification-v1.3.html
"""

from lxml import etree
from datetime import datetime
import re
from searx.url_utils import urlencode
from searx.utils import searx_useragent


categories = ['files']

api_key = None
base_url = None
search_string = 'api?t=search&apikey={api_key}&{query}'
min_seed = 1

# for some reason paging doesn't seem to work in jackett
paging = False
# number_of_results = 10


def request(query, params):
    # offset = (params['pageno'] - 1) * number_of_results
    search_path = search_string.format(
        query=urlencode({
            'q': query
            # 'limit': number_of_results,
            # 'offset': offset
        }), api_key=api_key)

    params['url'] = base_url + search_path

    return params


def response(resp):
    results = []

    search_results = etree.XML(resp.content)

    for item in search_results.xpath('./channel/item'):
        title = item.xpath('.//title')[0].text
        url = item.xpath('.//comments')[0].text
        size = item.xpath('.//size')[0].text
        magnet = item.xpath('.//link')[0].text
        content = item.xpath('.//description')[0].text
        pub_date_str = item.xpath('.//pubDate')[0].text
        pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')

        torznab_attrs = dict()
        for attribute in item:
            if attribute.tag == "{http://torznab.com/schemas/2015/feed}attr":
                torznab_attrs[str(attribute.get('name'))] = str(attribute.get('value'))
        seed = torznab_attrs['seeders']
        leech = torznab_attrs['peers']

        if not title:
            title = ""
        if not url:
            url = ""
        if not size:
            size = ""
        if not magnet:
            magnet = ""
        if not content:
            content = ""
        if not pub_date:
            pub_date = ""
        if not seed:
            seed = ""
        if not leech:
            leech = ""

        res_dict = {'url': url,
                    'title': title,
                    'publishedDate': pub_date,
                    'content': content,
                    'seed': seed,
                    'leech': leech,
                    'filesize': size,
                    'magnetlink': magnet}

        if int(seed) > min_seed:
            results.append(res_dict)

    return results
