"""
 Faroo (Web, News)

 @website     http://www.faroo.com
 @provide-api yes (http://www.faroo.com/hp/api/api.html), require API-key

 @using-api   no
 @results     JSON
 @stable      yes
 @parse       url, title, content, publishedDate, img_src
"""

from json import loads
import datetime
from searx.utils import searx_useragent
from searx.url_utils import urlencode

# engine dependent config
categories = ['general', 'news']
paging = True
language_support = True
number_of_results = 10

# search-url
url = 'http://www.faroo.com/'
search_url = url + 'instant.json?{query}'\
    '&start={offset}'\
    '&length={number_of_results}'\
    '&l={language}'\
    '&src={categorie}'\
    '&i=false'\
    '&c=false'

search_category = {'general': 'web',
                   'news': 'news'}


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * number_of_results + 1
    categorie = search_category.get(params['category'], 'web')

    if params['language'] == 'all':
        language = 'en'
    else:
        language = params['language'].split('_')[0]

    # if language is not supported, put it in english
    if language != 'en' and\
       language != 'de' and\
       language != 'zh':
        language = 'en'

    params['url'] = search_url.format(offset=offset,
                                      number_of_results=number_of_results,
                                      query=urlencode({'q': query}),
                                      language=language,
                                      categorie=categorie)

    params['headers']['Referer'] = url

    return params


# get response from search-request
def response(resp):
    # HTTP-Code 429: rate limit exceeded
    if resp.status_code == 429:
        raise Exception("rate limit has been exceeded!")

    results = []

    search_res = loads(resp.text)

    # return empty array if there are no results
    if not search_res.get('results', {}):
        return []

    # parse results
    for result in search_res['results']:
        publishedDate = None
        result_json = {'url': result['url'], 'title': result['title'],
                       'content': result['kwic']}
        if result['news']:
            result_json['publishedDate'] = \
                datetime.datetime.fromtimestamp(result['date'] / 1000.0)

        # append image result if image url is set
        if result['iurl']:
            result_json['template'] = 'videos.html'
            result_json['thumbnail'] = result['iurl']

        results.append(result_json)

    # return results
    return results
