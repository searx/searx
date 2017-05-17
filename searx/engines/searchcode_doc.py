"""
 Searchcode (It)

 @website     https://searchcode.com/
 @provide-api yes (https://searchcode.com/api/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""

from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['it']
paging = True

# search-url
url = 'https://searchcode.com/'
search_url = url + 'api/search_IV/?{query}&p={pageno}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}), pageno=params['pageno'] - 1)

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # parse results
    for result in search_results.get('results', []):
        href = result['url']
        title = "[{}] {} {}".format(result['type'], result['namespace'], result['name'])

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': result['description']})

    # return results
    return results
