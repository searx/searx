#!/usr/bin/env python

"""
 ArXiV (Scientific preprints)
 @website     https://arxiv.org
 @provide-api yes (export.arxiv.org/api/query)
 @using-api   yes
 @results     XML-RSS
 @stable      yes
 @parse       url, title, publishedDate, content
 More info on api: https://arxiv.org/help/api/user-manual
"""

from lxml import html
from datetime import datetime
from searx.utils import eval_xpath_list, eval_xpath_getindex


categories = ['science']
paging = True

base_url = 'https://export.arxiv.org/api/query?search_query=all:'\
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

    dom = html.fromstring(resp.content)

    for entry in eval_xpath_list(dom, '//entry'):
        title = eval_xpath_getindex(entry, './/title', 0).text

        url = eval_xpath_getindex(entry, './/id', 0).text

        content_string = '{doi_content}{abstract_content}'

        abstract = eval_xpath_getindex(entry, './/summary', 0).text

        #  If a doi is available, add it to the snipppet
        doi_element = eval_xpath_getindex(entry, './/link[@title="doi"]', 0, default=None)
        doi_content = doi_element.text if doi_element is not None else ''
        content = content_string.format(doi_content=doi_content, abstract_content=abstract)

        if len(content) > 300:
            content = content[0:300] + "..."
        # TODO: center snippet on query term

        publishedDate = datetime.strptime(eval_xpath_getindex(entry, './/published', 0).text, '%Y-%m-%dT%H:%M:%SZ')

        res_dict = {'url': url,
                    'title': title,
                    'publishedDate': publishedDate,
                    'content': content}

        results.append(res_dict)

    return results
