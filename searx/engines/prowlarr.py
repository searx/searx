# SPDX-License-Identifier: AGPL-3.0-or-later
"""

 Prowlarr search (Files)

"""

from json import loads
from urllib.parse import urlencode
from searx.exceptions import SearxEngineAPIException

categories = ['files']

paging = False
api_key = 'None'
indexer_ids = 'None'
search_type = 'search'
search_categories = 'None'
base_url = 'None'

def request(query, params):
    if base_url == 'None':
        raise SearxEngineAPIException('missing prowlarr base url')

    if api_key == 'None':
        raise SearxEngineAPIException('missing prowlarr API key')

    query_args = {
        'query': query,
        'apikey': api_key,
        'type': search_type
    }

    if indexer_ids != 'None':
        query_args['indexerIds'] = indexer_ids

    if search_categories != 'None':
        query_args['categories'] = search_categories

    params['url'] = base_url + urlencode(query_args)

    return params


def response(resp):
    results = []

    json_data = loads(resp.text)

    for result in json_data:

        newResult = {
            'title': result['title'],
            'url': result['infoUrl'],
            'template': 'torrent.html'
        }

        if 'files' in result:
            newResult['files'] = result['files']

        if 'size' in result:
            newResult['filesize'] = result['size']

        if 'seeders' in result:
            newResult['seed'] = result['seeders']

        if 'leechers' in result:
            newResult['leech'] = result['leechers']

        if 'downloadUrl' in result:
            newResult['torrentfile'] = result['downloadUrl']

        # magnet link *may* be in guid, but it may be also idential to infoUrl
        if 'guid' in result and isinstance(result['guid'], str) and result['guid'].startswith('magnet'):
            newResult['magnetlink'] = result['guid']

        results.append(newResult)

    return results
