# SPDX-License-Identifier: AGPL-3.0-or-later
"""

 Prowlarr search (Files)

"""

from json import loads
from urllib.parse import urlencode
from searx.exceptions import SearxEngineAPIException

categories = ''

paging = False
api_key = ''
indexer_ids = ''
search_type = 'search'
search_categories = ''
base_url = ''


def request(query, params):
    if not base_url:
        raise SearxEngineAPIException('missing prowlarr base url')

    if not api_key:
        raise SearxEngineAPIException('missing prowlarr API key')

    query_args = {
        'query': query,
        'apikey': api_key,
        'type': search_type
    }

    if indexer_ids:
        query_args['indexerIds'] = indexer_ids

    if search_categories:
        query_args['categories'] = search_categories

    params['url'] = base_url + urlencode(query_args)

    return params


def response(resp):
    results = []

    json_data = loads(resp.text)

    for result in json_data:

        new_result = {
            'title': result['title'],
            'url': result['infoUrl'],
            'template': 'torrent.html'
        }

        if 'files' in result:
            new_result['files'] = result['files']

        if 'size' in result:
            new_result['filesize'] = result['size']

        if 'seeders' in result:
            new_result['seed'] = result['seeders']

        if 'leechers' in result:
            new_result['leech'] = result['leechers']

        if 'downloadUrl' in result:
            new_result['torrentfile'] = result['downloadUrl']

        # magnet link *may* be in guid, but it may be also identical to infoUrl
        if 'guid' in result and isinstance(result['guid'], str) and result['guid'].startswith('magnet'):
            new_result['magnetlink'] = result['guid']

        results.append(new_result)

    return results
