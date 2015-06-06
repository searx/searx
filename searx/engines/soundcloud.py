"""
 Soundcloud (Music)

 @website     https://soundcloud.com
 @provide-api yes (https://developers.soundcloud.com/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content, publishedDate, embedded
"""

from json import loads
from urllib import urlencode, quote_plus
from dateutil import parser

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

embedded_url = '<iframe width="100%" height="166" ' +\
    'scrolling="no" frameborder="no" ' +\
    'data-src="https://w.soundcloud.com/player/?url={uri}"></iframe>'


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
            publishedDate = parser.parse(result['last_modified'])
            uri = quote_plus(result['uri'])
            embedded = embedded_url.format(uri=uri)

            # append result
            results.append({'url': result['permalink_url'],
                            'title': title,
                            'publishedDate': publishedDate,
                            'embedded': embedded,
                            'content': content})

    # return results
    return results
