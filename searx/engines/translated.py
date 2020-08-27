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
url = u'https://api.mymemory.translated.net/get?q={query}&langpair={from_lang}|{to_lang}{key}'
web_url = u'https://mymemory.translated.net/en/{from_lang}/{to_lang}/{query}'
weight = 100

parser_re = re.compile(b'.*?([a-z]+)-([a-z]+) (.{2,})$', re.I)
api_key = ''


def is_accepted(query, params):
    m = parser_re.match(query)
    if not m:
        return False

    params['parsed_regex'] = m
    from_lang, to_lang, query = m.groups()

    from_lang = is_valid_lang(from_lang)
    to_lang = is_valid_lang(to_lang)

    if not from_lang or not to_lang:
        return False

    params['from_lang'] = from_lang
    params['to_lang'] = to_lang
    params['query'] = query

    return True


def request(query, params):
    key_form = ''
    if api_key:
        key_form = '&key=' + api_key

    params['url'] = url.format(from_lang=params['from_lang'][2],
                               to_lang=params['to_lang'][2],
                               query=params['query'].decode('utf-8'))
                               key=key_form)

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
