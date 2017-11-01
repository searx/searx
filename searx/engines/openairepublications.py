#!/usr/bin/env python

"""
 OpenAIRE (publications) (Scholar publications)

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
import re
from searx.url_utils import urlencode


categories = ['science']
base_url = 'http://api.openaire.eu/search/publications?format=json'\
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
    res_dict = {}

    search_results = json.loads(resp.text)

    for entry in search_results['response']['results']['result']:
        entry_bis = entry['metadata']['oaf:entity']['oaf:result']
        title = entry_bis['title']['$']
        res_dict['title'] = title

        try:
            content = entry_bis['description']['$'][:300]
            if len(entry_bis['description']['$']) > 300:
                content += '...'
            res_dict['content'] = content
        except:
            pass

        try:
            publishedDate = datetime.strptime(entry_bis['dateofacceptance']['$'], '%Y-%m-%d')
        except:
            res_dict['publishedDate'] = publishedDate

        try:
            url = entry_bis['children']['instance']['webresource']['url']['$']
            res_dict['url'] = url
        except:
            pass

#        res_dict = {'url': url,
#                    'title': title,
#                    'publishedDate': publishedDate,
#                    'content': content}

        results.append(res_dict)

    return results
