"""
 YTS.mx Movies
 @website     https://yts.mx
 @provide-api yes (https://yts.mx/api)
 @using-api   yes
 @results     JSON (using REST api)
 @stable      yes (might change, but unlikely)
 @parse       url, title, content, seed, leech, filesize, torrentfile,  magnetlink, publishedDate, files
"""

import json
from urllib.parse import urlencode
from datetime import datetime

# engine dependent code
categories = ['files']
paging = False
language_support = False
time_range_support = False
offline = False

api_url = "https://yts.mx/api/v2/"
search_url = api_url + 'list_movies.json?{query}'


# construct api call url
def request(query, params):
    query = urlencode({'query_term': query})
    params['url'] = search_url.format(query=query)
    return params


# process response form search-request
def response(resp):
    results = []
    results_json = json.loads(resp.text)

    movies = results_json['data']['movies']

    for movie in movies:
        movie_name = movie['title_long']
        movie_url = movie['url']
        language = movie['language']
        torrents = movie['torrents']
        for torrent in torrents:
            torrent_url = torrent['url']
            seeds = torrent['seeds']
            leech = torrent['peers']
            file_size = torrent['size_bytes']
            quality = torrent['quality']
            date_ts = torrent['date_uploaded_unix']
            published_date = datetime.utcfromtimestamp(date_ts) #.strftime('%Y-%m-%d %H:%M:%S')
            torrent_hash = torrent['hash']
            magnet_link = 'magnet:?xt=urn:btih:' + torrent_hash

            params = {
                'url': movie_url,
                'title': f"{movie_name} [{quality}] ({language})",
                'seed': seeds,
                'leech': leech,
                'template': 'torrent.html',
                'filesize': file_size,
                'magnetlink': magnet_link,
                'torrentfile': torrent_url,
                'publishedDate': published_date
            }
            results.append(params)
        params['files'] = len(results)
    return results
