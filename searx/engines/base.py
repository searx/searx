#!/usr/bin/env python

"""
 BASE (Scholar publications)

 @website     https://base-search.net
 @provide-api yes with authorization (https://api.base-search.net/)

 @using-api   yes
 @results     XML
 @stable      ?
 @parse       url, title, publishedDate, content
 More info on api: http://base-search.net/about/download/base_interface.pdf
"""

from lxml import etree
from datetime import datetime
import re
from searx.url_utils import urlencode
from searx.utils import searx_useragent


categories = ['science']

base_url = 'https://api.base-search.net/cgi-bin/BaseHttpSearchInterface.fcgi'\
           + '?func=PerformSearch&{query}&boost=oa&hits={hits}&offset={offset}'

# engine dependent config
paging = True
number_of_results = 10

# shortcuts for advanced search
shorcut_dict = {
    # user-friendly keywords
    'format:': 'dcformat:',
    'author:': 'dccreator:',
    'collection:': 'dccollection:',
    'hdate:': 'dchdate:',
    'contributor:': 'dccontributor:',
    'coverage:': 'dccoverage:',
    'date:': 'dcdate:',
    'abstract:': 'dcdescription:',
    'urls:': 'dcidentifier:',
    'language:': 'dclanguage:',
    'publisher:': 'dcpublisher:',
    'relation:': 'dcrelation:',
    'rights:': 'dcrights:',
    'source:': 'dcsource:',
    'subject:': 'dcsubject:',
    'title:': 'dctitle:',
    'type:': 'dcdctype:'
}


def request(query, params):
    # replace shortcuts with API advanced search keywords
    for key in shorcut_dict.keys():
        query = re.sub(str(key), str(shorcut_dict[key]), query)

    # basic search
    offset = (params['pageno'] - 1) * number_of_results

    string_args = dict(query=urlencode({'query': query}),
                       offset=offset,
                       hits=number_of_results)

    params['url'] = base_url.format(**string_args)

    params['headers']['User-Agent'] = searx_useragent()
    return params


def response(resp):
    results = []

    search_results = etree.XML(resp.text)

    for entry in search_results.xpath('./result/doc'):
        content = "No description available"

        date = datetime.now()  # needed in case no dcdate is available for an item
        for item in entry:
            if item.attrib["name"] == "dchdate":
                harvestDate = item.text

            elif item.attrib["name"] == "dcdate":
                date = item.text

            elif item.attrib["name"] == "dctitle":
                title = item.text

            elif item.attrib["name"] == "dclink":
                url = item.text

            elif item.attrib["name"] == "dcdescription":
                content = item.text[:300]
                if len(item.text) > 300:
                    content += "..."

# dates returned by the BASE API are not several formats
        publishedDate = None
        for date_format in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                publishedDate = datetime.strptime(date, date_format)
                break
            except:
                pass

        if publishedDate is not None:
            res_dict = {'url': url,
                        'title': title,
                        'publishedDate': publishedDate,
                        'content': content}
        else:
            res_dict = {'url': url,
                        'title': title,
                        'content': content}

        results.append(res_dict)

    return results
