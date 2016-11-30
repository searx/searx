# Yacy (Web, Images, Videos, Music, Files)
#
# @website     http://yacy.net
# @provide-api yes
#              (http://www.yacy-websuche.de/wiki/index.php/Dev:APIyacysearch)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       (general)    url, title, content, publishedDate
# @parse       (images)     url, title, img_src
#
# @todo        parse video, audio and file results

from json import loads
from dateutil import parser
from searx.url_utils import urlencode

from searx.utils import html_to_text

# engine dependent config
categories = ['general', 'images']  # TODO , 'music', 'videos', 'files'
paging = True
language_support = True
number_of_results = 5

# search-url
base_url = 'http://localhost:8090'
search_url = '/yacysearch.json?{query}'\
             '&startRecord={offset}'\
             '&maximumRecords={limit}'\
             '&contentdom={search_type}'\
             '&resource=global'

# yacy specific type-definitions
search_types = {'general': 'text',
                'images': 'image',
                'files': 'app',
                'music': 'audio',
                'videos': 'video'}


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * number_of_results
    search_type = search_types.get(params.get('category'), '0')

    params['url'] = base_url +\
        search_url.format(query=urlencode({'query': query}),
                          offset=offset,
                          limit=number_of_results,
                          search_type=search_type)

    # add language tag if specified
    if params['language'] != 'all':
        params['url'] += '&lr=lang_' + params['language'].split('-')[0]

    return params


# get response from search-request
def response(resp):
    results = []

    raw_search_results = loads(resp.text)

    # return empty array if there are no results
    if not raw_search_results:
        return []

    search_results = raw_search_results.get('channels', [])

    if len(search_results) == 0:
        return []

    for result in search_results[0].get('items', []):
        # parse image results
        if result.get('image'):
            # append result
            results.append({'url': result['url'],
                            'title': result['title'],
                            'content': '',
                            'img_src': result['image'],
                            'template': 'images.html'})

        # parse general results
        else:
            publishedDate = parser.parse(result['pubDate'])

            # append result
            results.append({'url': result['link'],
                            'title': result['title'],
                            'content': html_to_text(result['description']),
                            'publishedDate': publishedDate})

        # TODO parse video, audio and file results

    # return results
    return results
