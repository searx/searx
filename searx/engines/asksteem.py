"""
 Asksteem (general)

 @website     https://asksteem.com/
 @provide-api yes

 @using-api   yes
 @results     JSON (https://github.com/Hoxly/asksteem-docs/wiki)
 @stable      yes
 @parse       url, title, content
"""

from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['general']
paging = True
language_support = False
disabled = True

# search-url
search_url = 'https://api.asksteem.com/search?{params}'
result_url = 'https://steemit.com/@{author}/{title}'


# do search-request
def request(query, params):
    url = search_url.format(params=urlencode({'q': query, 'pg': params['pageno']}))
    params['url'] = url
    return params

# get response from search-request
def response(resp):
    json = loads(resp.text)

    results = []

    for result in json.get('results', []):
        results.append({'url': result_url.format(author=result['author'], title=result['permlink']),
                        'title': result['title'],
                        'content': result['summary']})
    return results
