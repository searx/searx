#!/usr/bin/env python

"""
 OpenAIRE (datasets) (Research datasets)

 @website     https://openaire.eu
 @provide-api yes (http://api.openaire.eu/)

 @using-api   yes
 @results     json
 @stable      yes
 @parse       url, title, publishedDate, content
 More info on api: http://api.openaire.eu/
"""

import json
from datetime import datetime
from searx.url_utils import urlencode


categories = ['science']
base_url = 'http://api.openaire.eu/search/datasets?format=json'\
           + '&page={offset}&size={number_of_results}&title={query}'

# engine dependent config
paging = True
number_of_results = 10


def request(query, params):
    offset = params['pageno']

    string_args = dict(query=query,
                       offset=offset,
                       number_of_results=number_of_results)

    params['url'] = base_url.format(**string_args)
    return params


def response(resp):
    results = []

    search_results = json.loads(resp.text)

    for entry in search_results['response']['results']['result']:
        entry_bis = entry['metadata']['oaf:entity']['oaf:result']
        title = entry_bis['title']['$']

        content = entry_bis['description']['$'][:300]
        if len(entry_bis['description']['$']) > 300:
            content += '...'

        publishedDate = datetime.strptime(entry_bis['dateofacceptance']['$'], '%Y-%m-%d')

        url = entry_bis['children']['instance']['webresource']['url']['$']

        res_dict = {'url': url,
                    'title': title,
                    'publishedDate': publishedDate,
                    'content': content}

        results.append(res_dict)

    return results
