"""
 Bidb Arama

 @website     https://bidb.itu.edu.tr/
 @provide-api ?
 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from lxml import html
from searx import logger
from searx.url_utils import urlencode

logger = logger.getChild('bidb engine')

# engine dependent config
categories = ['general']
paging = True
language_support = False  # TODO

# search-url
base_url = 'https://bidb.itu.edu.tr/'
search_url = 'arama-sonuc-v2/page/{page}?indexCatalogue=aramabidb&searchQuery={query}'

results_xpath = '//dl[contains(@class, "sfsearchResultsWrp")]'
url_xpath = '//dt[@class="sfsearchResultTitle"]/a/@href'
title_xpath = '//dt[@class="sfsearchResultTitle"]/a/text()'
content_xpath = '//dt[@class="sfsearchResultTitle"]/a/@href'


def request(query, params):
    #lang = params['language'].split('-')[0]
    #host = base_url #.format(tld=language_map.get(lang) or default_tld)
    params['url'] = base_url + search_url.format(page=params['pageno'], query=query)
    return params


# get response from search-request
def response(resp):
    dom = html.fromstring(resp.text)
    results = []

    for result in range(10):
        try:
            res = {'url': dom.xpath(url_xpath)[result],
                   'title': ''.join(dom.xpath(title_xpath)[result]),
                   'content': ''.join(dom.xpath(content_xpath)[result])}
        except:
            logger.exception('bidb parse crash')
                                                 
            continue

        results.append(res)

    return results
