# Node Package Manager
#
# @website     https://www.npmjs.com/
# @provide-api yes (https://api-docs.npms.io/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content

from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['it']
paging = True
language_support = False

# search-url
base_url = 'https://api.npms.io/v2/search'
search_url = base_url + '?{query}&size=25&from={offset}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 25

    params['url'] = search_url.format(query=urlencode({'q': query}), offset=offset)

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # return empty array if there are no results
    if 'results' not in search_results:
        return []

    # parse results
    for res in search_results['results']:
        package = res['package']

        title = package['name']
        url = package['links']['npm']

        if package['description']:
            content = package['description'][:400]
        else:
            content = ''

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
