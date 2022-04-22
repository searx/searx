from urllib.parse import urlencode
import json
import re

categories = ['general']  # optional

base_url = 'https://api.ipfs-search.com/v1/'
search_string = 'search?{query}&page={page}'

ipfs_url = 'https://gateway.ipfs.io/ipfs/{hash}'


def request(query, params):

    search_path = search_string.format(
        query=urlencode({'q': query}),
        page=params['pageno'])

    params['url'] = base_url + search_path

    return params


def response(resp):
    api_results = json.loads(resp.text)
    results = []
    for result in api_results['hits']:
        url = ipfs_url.format(hash=result['hash'])
        title = re.sub(re.compile('<.*?>'), '', result['title'])
        description = result['description']

        results.append({'url': url,
                        'title': title,
                        'content': description})

    return results
