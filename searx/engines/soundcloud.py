## Soundcloud (Music)
#
# @website     https://soundcloud.com
# @provide-api yes (https://developers.soundcloud.com/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content

from json import loads
from urllib import urlencode

# engine dependent config
categories = ['music']
paging = True

# api-key
guest_client_id = 'b45b1aa10f1ac2941910a7f0d10f8e28'

# search-url
url = 'https://api.soundcloud.com/'
search_url = url + 'search?{query}'\
                         '&facet=model'\
                         '&limit=20'\
                         '&offset={offset}'\
                         '&linked_partitioning=1'\
                         '&client_id={client_id}'   # noqa


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 20

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      offset=offset,
                                      client_id=guest_client_id)

    return params


# get response from search-request
def response(resp):
    results = []

    search_res = loads(resp.text)

    # parse results
    for result in search_res.get('collection', []):
        if result['kind'] in ('track', 'playlist'):
            title = result['title']
            content = result['description']

            # append result
            results.append({'url': result['permalink_url'],
                            'title': title,
                            'content': content})

    # return results
    return results
