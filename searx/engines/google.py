## Google (Web)
# 
# @website     https://www.google.com
# @provide-api yes (https://developers.google.com/web-search/docs/), deprecated!
# 
# @using-api   yes
# @results     JSON
# @stable      yes (but deprecated)
# @parse       url, title, content

from urllib import urlencode
from json import loads

# engine dependent config
categories = ['general']
paging = True
language_support = True

# search-url
url = 'https://ajax.googleapis.com/'
search_url = url + 'ajax/services/search/web?v=2.0&start={offset}&rsz=large&safe=off&filter=off&{query}&hl={language}'  # noqa


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 8

    language = 'en-US'
    if params['language'] != 'all':
        language = params['language'].replace('_', '-')

    params['url'] = search_url.format(offset=offset,
                                      query=urlencode({'q': query}),
                                      language=language)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # return empty array if there are no results
    if not search_res.get('responseData', {}).get('results'):
        return []

    # parse results
    for result in search_res['responseData']['results']:
        # append result
        results.append({'url': result['unescapedUrl'],
                        'title': result['titleNoFormatting'],
                        'content': result['content']})

    # return results
    return results
