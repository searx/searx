## Github (It)
#
# @website     https://github.com/
# @provide-api yes (https://developer.github.com/v3/)
#
# @using-api   yes
# @results     JSON
# @stable      yes (using api)
# @parse       url, title, content

from __future__ import absolute_import
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()

from urllib.parse import urlencode
from json import loads
from cgi import escape

# engine dependent config
categories = ['it']

# search-url
search_url = 'https://api.github.com/search/repositories?sort=stars&order=desc&{query}'  # noqa

accept_header = 'application/vnd.github.preview.text-match+json'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))

    params['headers']['Accept'] = accept_header

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # check if items are recieved
    if not 'items' in search_res:
        return []

    # parse results
    for res in search_res['items']:
        title = res['name']
        url = res['html_url']

        if res['description']:
            content = escape(res['description'][:500])
        else:
            content = ''

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content})

    # return results
    return results
