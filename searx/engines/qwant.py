"""
 Qwant (Web, Images, News, Social)

 @website     https://qwant.com/
 @provide-api not officially (https://api.qwant.com/api/search/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""

from datetime import datetime
from json import loads
from searx.utils import html_to_text
from searx.url_utils import urlencode
from searx.utils import match_language

# engine dependent config
categories = None
paging = True
language_support = True
supported_languages_url = 'https://qwant.com/region'

category_to_keyword = {'general': 'web',
                       'images': 'images',
                       'news': 'news',
                       'social media': 'social'}

# search-url
url = 'https://api.qwant.com/api/search/{keyword}?count=10&offset={offset}&f=&{query}&t={keyword}&uiv=4'


# do search-request
def request(query, params):
    offset = (params['pageno'] - 1) * 10

    if categories[0] and categories[0] in category_to_keyword:

        params['url'] = url.format(keyword=category_to_keyword[categories[0]],
                                   query=urlencode({'q': query}),
                                   offset=offset)
    else:
        params['url'] = url.format(keyword='web',
                                   query=urlencode({'q': query}),
                                   offset=offset)

    # add language tag
    if params['language'] != 'all':
        language = match_language(params['language'], supported_languages, language_aliases)
        params['url'] += '&locale=' + language.replace('-', '_').lower()

    params['headers']['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
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

        title = html_to_text(result['title'])
        res_url = result['url']
        content = html_to_text(result['desc'])

        if category_to_keyword.get(categories[0], '') == 'web':
            results.append({'title': title,
                            'content': content,
                            'url': res_url})

        elif category_to_keyword.get(categories[0], '') == 'images':
            thumbnail_src = result['thumbnail']
            img_src = result['media']
            results.append({'template': 'images.html',
                            'url': res_url,
                            'title': title,
                            'content': '',
                            'thumbnail_src': thumbnail_src,
                            'img_src': img_src})

        elif category_to_keyword.get(categories[0], '') == 'social':
            published_date = datetime.fromtimestamp(result['date'], None)
            img_src = result.get('img', None)
            results.append({'url': res_url,
                            'title': title,
                            'publishedDate': published_date,
                            'content': content,
                            'img_src': img_src})

        elif category_to_keyword.get(categories[0], '') == 'news':
            published_date = datetime.fromtimestamp(result['date'], None)
            media = result.get('media', [])
            if len(media) > 0:
                img_src = media[0].get('pict', {}).get('url', None)
            else:
                img_src = None
            results.append({'url': res_url,
                            'title': title,
                            'publishedDate': published_date,
                            'content': content,
                            'img_src': img_src})

    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    # list of regions is embedded in page as a js object
    response_text = resp.text
    response_text = response_text[response_text.find('regionalisation'):]
    response_text = response_text[response_text.find('{'):response_text.find(');')]

    regions_json = loads(response_text)

    supported_languages = []
    for lang in regions_json['languages'].values():
        if lang['code'] == 'nb':
            lang['code'] = 'no'
        for country in lang['countries']:
            supported_languages.append(lang['code'] + '-' + country)

    return supported_languages
