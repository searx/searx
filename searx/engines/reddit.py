"""
 Reddit

 @website      https://www.reddit.com/
 @provide-api  yes (https://www.reddit.com/dev/api)

 @using-api    yes
 @results      JSON
 @stable       yes
 @parse        url, title, content, thumbnail, publishedDate
"""

import json
from cgi import escape
from urllib import urlencode
from urlparse import urlparse
from datetime import datetime

# engine dependent config
categories = ['general', 'images', 'news', 'social media']
page_size = 25

# search-url
search_url = 'https://www.reddit.com/search.json?{query}'


# do search-request
def request(query, params):
    query = urlencode({'q': query,
                       'limit': page_size})
    params['url'] = search_url.format(query=query)

    return params


# get response from search-request
def response(resp):
    img_results = []
    text_results = []

    search_results = json.loads(resp.text)

    # return empty array if there are no results
    if 'data' not in search_results:
        return []

    posts = search_results.get('data', {}).get('children', [])

    # process results
    for post in posts:
        data = post['data']

        # extract post information
        params = {
            'url': data['url'],
            'title': data['title']
        }

        # if thumbnail field contains a valid URL, we need to change template
        thumbnail = data['thumbnail']
        url_info = urlparse(thumbnail)
        # netloc & path
        if url_info[1] != '' and url_info[2] != '':
            params['thumbnail_src'] = thumbnail
            params['template'] = 'images.html'
            img_results.append(params)
        else:
            created = datetime.fromtimestamp(data['created_utc'])
            params['content'] = escape(data['selftext'])
            params['publishedDate'] = created
            text_results.append(params)

    # show images first and text results second
    return img_results + text_results
