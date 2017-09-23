#!/usr/bin/env python

"""
 ArXiV (Scientific preprints)
 @website     https://axiv.org
 @provide-api yes (export.arxiv.org/api/query)
 @using-api   yes
 @results     XML-RSS
 @stable      yes
 @parse       url, title, publishedDate, content
 More info on api: https://arxiv.org/help/api/user-manual
"""

from lxml import html
from datetime import datetime
from searx.url_utils import urlencode


categories = ['science']

base_url = 'http://export.arxiv.org/api/query?search_query=all:'\
           + '{query}&start={offset}&max_results={number_of_results}'

# engine dependent config
number_of_results = 10


def request(query, params):
    # basic search
    offset = (params['pageno'] - 1) * number_of_results

    string_args = dict(query=query,
                       offset=offset,
                       number_of_results=number_of_results)

    params['url'] = base_url.format(**string_args)

    return params


def response(resp):
    results = []

    search_results = html.fromstring(resp.text.encode('utf-8')).xpath('//entry')

    for entry in search_results:
        title = entry.xpath('.//title')[0].text

        url = entry.xpath('.//id')[0].text

        content = entry.xpath('.//summary')[0].text

        #  If a doi is available, add it to the snipppet
        try:
            doi = entry.xpath('.//link[@title="doi"]')[0].text
            content = 'DOI: ' + doi + ' Abstract: ' + content
        except:
            pass

        if len(content) > 300:
                    content = content[0:300] + "..."
        # TODO: center snippet on query term

        publishedDate = datetime.strptime(entry.xpath('.//published')[0].text, '%Y-%m-%dT%H:%M:%SZ')

        res_dict = {'url': url,
                    'title': title,
                    'publishedDate': publishedDate,
                    'content': content}

        results.append(res_dict)

    return results
