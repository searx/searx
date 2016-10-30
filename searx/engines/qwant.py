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
from urllib import urlencode

from searx.utils import html_to_text

# engine dependent config
categories = None
paging = True
language_support = True
supported_languages = ["fr-FR", "de-DE", "en-GB", "it-IT", "es-ES", "pt-PT", "de-CH", "fr-CH", "it-CH", "de-AT",
                       "fr-BE", "nl-BE", "nl-NL", "da-DK", "fi-FI", "sv-SE", "en-IE", "no-NO", "pl-PL", "ru-RU",
                       "el-GR", "bg-BG", "cs-CZ", "et-EE", "hu-HU", "ro-RO", "en-US", "en-CA", "fr-CA", "pt-BR",
                       "es-AR", "es-CL", "es-MX", "ja-JP", "en-SG", "en-IN", "en-MY", "ms-MY", "ko-KR", "tl-PH",
                       "th-TH", "he-IL", "tr-TR", "en-AU", "en-NZ"]

category_to_keyword = {'general': 'web',
                       'images': 'images',
                       'news': 'news',
                       'social media': 'social'}

# search-url
url = 'https://api.qwant.com/api/search/{keyword}?count=10&offset={offset}&f=&{query}'


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

    # add language tag if specified
    if params['language'] != 'all':
        locale = params['language'].split('-')
        if len(locale) == 2 and params['language'] in supported_languages:
            params['url'] += '&locale=' + params['language'].replace('-', '_').lower()
        else:
            # try to get a country code for language
            for lang in supported_languages:
                if locale[0] == lang.split('-')[0]:
                    params['url'] += '&locale=' + lang.replace('-', '_').lower()
                    break

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

        elif (category_to_keyword.get(categories[0], '') == 'news' or
              category_to_keyword.get(categories[0], '') == 'social'):
            published_date = datetime.fromtimestamp(result['date'], None)

            results.append({'url': res_url,
                            'title': title,
                            'publishedDate': published_date,
                            'content': content})

    # return results
    return results
