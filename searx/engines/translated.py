"""
 MyMemory Translated

 @website     https://mymemory.translated.net/
 @provide-api yes (https://mymemory.translated.net/doc/spec.php)
 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""

engine_type = 'online_dictionnary'
categories = ['general']
url = 'https://api.mymemory.translated.net/get?q={query}&langpair={from_lang}|{to_lang}{key}'
web_url = 'https://mymemory.translated.net/en/{from_lang}/{to_lang}/{query}'
weight = 100
https_support = True

api_key = ''


def request(query, params):
    if api_key:
        key_form = '&key=' + api_key
    else:
        key_form = ''
    params['url'] = url.format(from_lang=params['from_lang'][1],
                               to_lang=params['to_lang'][1],
                               query=params['query'],
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
