# SPDX-License-Identifier: AGPL-3.0-or-later

"""
IMDB - Internet Movie Database
Retrieves results from a basic search
Advanced search options are not supported
"""

import json

about = {
    "website": 'https://imdb.com/',
    "wikidata_id": 'Q37312',
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

categories = ['general']
paging = False
base_url = 'https://imdb.com/{category}/{id}'
suggestion_url = "https://v2.sg.media-imdb.com/suggestion/{letter}/{query}.json"
search_categories = {
    "nm": "name",
    "tt": "title",
    "kw": "keyword",
    "co": "company",
    "ep": "episode"
}


def request(query, params):
    query = query.replace(" ", "_").lower()
    params['url'] = suggestion_url.format(letter=query[0], query=query)
    return params


def response(resp):
    suggestions = json.loads(resp.text)
    results = []
    for entry in suggestions['d']:
        content = ""
        if entry['id'][:2] in search_categories:
            href = base_url.format(category=search_categories[entry['id'][:2]], id=entry['id'])
        if 'y' in entry:
            content += str(entry['y']) + " - "
        if 's' in entry:
            content += entry['s']
        results.append({
            "title": entry['l'],
            "url": href,
            "content": content
        })
    return results
