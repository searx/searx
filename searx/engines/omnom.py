# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Omnom (General)
"""

from json import loads
from urllib.parse import urlencode

# about
about = {
    "website": 'https://github.com/asciimoo/omnom',
    "wikidata_id": None,
    "official_api_documentation": 'http://your.omnom.host/api',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ['general']
paging = True

# search-url
base_url = None
search_path = 'bookmarks?{query}&pageno={pageno}&format=json'
bookmark_path = 'bookmark?id='


# do search-request
def request(query, params):
    params['url'] = base_url +\
        search_path.format(query=urlencode({'query': query}),
                           pageno=params['pageno'])

    return params


# get response from search-request
def response(resp):
    results = []
    json = loads(resp.text)

    # parse results
    for r in json.get('Bookmarks', {}):
        content = r['url']
        if r.get('notes'):
            content += ' - ' + r['notes']
        results.append({
            'title': r['title'],
            'content': content,
            'url': base_url + bookmark_path + str(r['id']),
        })

    # return results
    return results
