"""
 Qwant (Web, Images, News, Social)

 @website     https://qwant.com/
 @provide-api not officially (https://api.qwant.com/api/search/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""

from urllib import urlencode
from json import loads
from datetime import datetime

# engine dependent config
categories = None
paging = True
language_support = True

search_url_keyword = None

# search-url
url = 'https://api.qwant.com/api/search/{keyword}?count=10&offset={offset}&f=&{query}'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    params['url'] = url.format(keyword=search_url_keyword,
                               query=urlencode({'q': query}),
                               offset=offset)

    # add language tag if specified
    if params['language'] != 'all':
        params['url'] += '&locale=' + params['language'].lower()

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # return empty array if there are no results
    if 'data' not in search_results:
        return []

    data = search_results.get('data', {})

    res = data.get('result', {})

    # parse results
    for result in res.get('items', {}):

        title = result['title']
        res_url = result['url']
        content = result['desc']

        if search_url_keyword == 'web':
            results.append({'title': title,
                            'content': content,
                            'url': res_url})

        elif search_url_keyword == 'images':
            thumbnail_src = result['thumbnail']
            img_src = result['media']
            results.append({'template': 'images.html',
                            'url': res_url,
                            'title': title,
                            'content': '',
                            'thumbnail_src': thumbnail_src,
                            'img_src': img_src})

        elif search_url_keyword == 'news' or search_url_keyword == 'social':
            published_date = datetime.fromtimestamp(result['date'], None)

            results.append({'url': res_url,
                            'title': title,
                            'publishedDate': published_date,
                            'content': content})

    # return results
    return results
