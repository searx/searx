# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Semantic Scholar (Science)
"""

from json import dumps, loads

from searx import logger


logger = logger.getChild('semantic scholar')
search_url = 'https://www.semanticscholar.org/api/1/search'


def request(query, params):
    params['url'] = search_url
    params['method'] = 'POST'
    params['headers']['content-type'] = 'application/json'
    params['data'] = dumps({
        "queryString": query,
        "page": params['pageno'],
        "pageSize": 10,
        "sort": "relevance",
        "useFallbackRankerService": False,
        "useFallbackSearchCluster": False,
        "getQuerySuggestions": False,
        "authors": [],
        "coAuthors": [],
        "venues": [],
        "performTitleMatch": True,
    })
    return params


def response(resp):
    res = loads(resp.text)
    results = []
    for result in res['results']:
        if 'primaryPaperLink' not in result or 'url' not in result['primaryPaperLink']:
            logger.debug('ignore result because of missing link: %s', result)
            continue

        results.append({
            'url': result['primaryPaperLink']['url'],
            'title': result['title']['text'],
            'content': result['paperAbstractTruncated']
        })

    return results
