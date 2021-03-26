# SPDX-License-Identifier: AGPL-3.0-or-later
"""

Core Engine (science)

"""

from json import loads
from datetime import datetime
from urllib.parse import urlencode

about = {
    "website": 'https://core.ac.uk',
    "wikidata_id": 'Q22661180',
    "official_api_documentation": 'https://core.ac.uk/documentation/api/',
    "use_official_api": True,
    "require_api_key": True,
    "results": 'JSON',
}

categories = ['science']

paging = True
nb_per_page = 20


# apikey = ''
apikey = 'MVBozuTX8QF9I1D0GviL5bCn2Ueat6NS'


base_url = 'https://core.ac.uk:443/api-v2/search/'
search_string = '{query}?page={page}&pageSize={nb_per_page}&apiKey={apikey}'


def request(query, params):

    search_path = search_string.format(
        query=urlencode({'q': query}),
        nb_per_page=nb_per_page,
        page=params['pageno'],
        apikey=apikey)

    params['url'] = base_url + search_path
    return params


def response(resp):
    results = []

    json_data = loads(resp.text)
    for result in json_data['data']:
        time = result['_source']['publishedDate']
        if time is None:
            date = datetime.now()
        else:
            date = datetime.fromtimestamp(time / 1000)
        results.append({
            'url': result['_source']['urls'][0],
            'title': result['_source']['title'],
            'content': result['_source']['description'],
            'publishedDate': date})

    return results
