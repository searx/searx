## Searchcode (It)
#
# @website     https://searchcode.com/
# @provide-api yes (https://searchcode.com/api/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urlencode
from json import loads

# engine dependent config
categories = ['it']
paging = True

# search-url
url = 'https://searchcode.com/'
search_url = url+'api/search_IV/?{query}&p={pageno}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      pageno=params['pageno']-1)

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # parse results
    for result in search_results['results']:
        href = result['url']
        title = "[" + result['type'] + "] " +\
                result['namespace'] +\
                " " + result['name']
        content = '<span class="highlight">[' +\
                  result['type'] + "] " +\
                  result['name'] + " " +\
                  result['synopsis'] +\
                  "</span><br />" +\
                  result['description']

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content})

    # return results
    return results
