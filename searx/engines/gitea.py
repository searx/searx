"""
 Gitea (It)

 @website     https://teahub.io/

 @using-api   yes
 @results     JSON
 @stable      yes (using api)
 @parse       url, title, content
"""

from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['it']

# search-url
search_url = 'https://teahub.io/api/v1/repos/search?{query}&limit=50'  # noqa


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # check if items are recieved
    if 'data' not in search_res:
        return []

    # parse results
    for res in search_res['data']:
        title = res['name']
        url = res['html_url']

        if res['description']:
            content = res['description'][:500]
        else:
            content = ''

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
