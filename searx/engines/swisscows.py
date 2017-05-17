"""
 Swisscows (Web, Images)

 @website     https://swisscows.ch
 @provide-api no

 @using-api   no
 @results     HTML (using search portal)
 @stable      no (HTML can change)
 @parse       url, title, content
"""

from json import loads
import re
from lxml.html import fromstring
from searx.url_utils import unquote, urlencode

# engine dependent config
categories = ['general', 'images']
paging = True
language_support = True

# search-url
base_url = 'https://swisscows.ch/'
search_string = '?{query}&page={page}'

supported_languages_url = base_url

# regex
regex_json = re.compile(b'initialData: {"Request":(.|\n)*},\s*environment')
regex_json_remove_start = re.compile(b'^initialData:\s*')
regex_json_remove_end = re.compile(b',\s*environment$')
regex_img_url_remove_start = re.compile(b'^https?://i\.swisscows\.ch/\?link=')


# do search-request
def request(query, params):
    if params['language'] == 'all':
        ui_language = 'browser'
        region = 'browser'
    elif params['language'].split('-')[0] == 'no':
        region = 'nb-NO'
    else:
        region = params['language']
        ui_language = params['language'].split('-')[0]

    search_path = search_string.format(
        query=urlencode({'query': query, 'uiLanguage': ui_language, 'region': region}),
        page=params['pageno']
    )

    # image search query is something like 'image?{query}&page={page}'
    if params['category'] == 'images':
        search_path = 'image' + search_path

    params['url'] = base_url + search_path

    return params


# get response from search-request
def response(resp):
    results = []

    json_regex = regex_json.search(resp.text)

    # check if results are returned
    if not json_regex:
        return []

    json_raw = regex_json_remove_end.sub(b'', regex_json_remove_start.sub(b'', json_regex.group()))
    json = loads(json_raw.decode('utf-8'))

    # parse results
    for result in json['Results'].get('items', []):
        result_title = result['Title'].replace(u'\uE000', '').replace(u'\uE001', '')

        # parse image results
        if result.get('ContentType', '').startswith('image'):
            img_url = unquote(regex_img_url_remove_start.sub(b'', result['Url'].encode('utf-8')).decode('utf-8'))

            # append result
            results.append({'url': result['SourceUrl'],
                            'title': result['Title'],
                            'content': '',
                            'img_src': img_url,
                            'template': 'images.html'})

        # parse general results
        else:
            result_url = result['Url'].replace(u'\uE000', '').replace(u'\uE001', '')
            result_content = result['Description'].replace(u'\uE000', '').replace(u'\uE001', '')

            # append result
            results.append({'url': result_url,
                            'title': result_title,
                            'content': result_content})

    # parse images
    for result in json.get('Images', []):
        # decode image url
        img_url = unquote(regex_img_url_remove_start.sub(b'', result['Url'].encode('utf-8')).decode('utf-8'))

        # append result
        results.append({'url': result['SourceUrl'],
                        'title': result['Title'],
                        'content': '',
                        'img_src': img_url,
                        'template': 'images.html'})

    # return results
    return results


# get supported languages from their site
def _fetch_supported_languages(resp):
    supported_languages = []
    dom = fromstring(resp.text)
    options = dom.xpath('//div[@id="regions-popup"]//ul/li/a')
    for option in options:
        code = option.xpath('./@data-val')[0]
        if code.startswith('nb-'):
            code = code.replace('nb', 'no', 1)
        supported_languages.append(code)

    return supported_languages
