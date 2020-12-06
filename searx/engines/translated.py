"""
 MyMemory Translated

 @website     https://mymemory.translated.net/
 @provide-api yes (https://mymemory.translated.net/doc/spec.php)
 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""
import re
from searx.utils import is_valid_lang

categories = ['general']
url = 'https://api.mymemory.translated.net/get?q={query}&langpair={from_lang}|{to_lang}{key}'
web_url = 'https://mymemory.translated.net/en/{from_lang}/{to_lang}/{query}'
weight = 100
https_support = True

parser_re = re.compile('.*?([a-z]+)-([a-z]+) (.{2,})$', re.I)
api_key = ''


def request(query, params):
    m = parser_re.match(query)
    if not m:
        return params

    from_lang, to_lang, query = m.groups()

    from_lang = is_valid_lang(from_lang)
    to_lang = is_valid_lang(to_lang)

    if not from_lang or not to_lang:
        return params

    if api_key:
        key_form = '&key=' + api_key
    else:
        key_form = ''
    params['url'] = url.format(from_lang=from_lang[1],
                               to_lang=to_lang[1],
                               query=query,
                               key=key_form)
    params['query'] = query
    params['from_lang'] = from_lang
    params['to_lang'] = to_lang

    return params


def response(resp):
    results = []
    results.append({
        'url': web_url.format(
            from_lang=resp.search_params['from_lang'][2],
            to_lang=resp.search_params['to_lang'][2],
            query=resp.search_params['query']),
        'title': '[{0}-{1}] {2}'.format(
            resp.search_params['from_lang'][1],
            resp.search_params['to_lang'][1],
            resp.search_params['query']),
        'content': resp.json()['responseData']['translatedText']
    })
    return results
