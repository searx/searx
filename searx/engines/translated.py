import re
from urlparse import urljoin
from lxml import html
from cgi import escape
from searx.engines.xpath import extract_text
from searx.languages import language_codes

categories = ['general']
url = 'http://api.mymemory.translated.net/get?q={query}&langpair={from_lang}|{to_lang}'
web_url = 'http://mymemory.translated.net/en/{from_lang}/{to_lang}/{query}'
weight = 100

parser_re = re.compile(u'.*?([a-z]+)-([a-z]+) (.{2,})$', re.I)

def is_valid_lang(lang):
    is_abbr = (len(lang) == 2)
    if is_abbr:
        for l in language_codes:
            if l[0][:2] == lang.lower():
                return (True, l[0][:2], l[1].lower())
        return False
    else:
        for l in language_codes:
            if l[1].lower() == lang.lower():
                return (True, l[0][:2], l[1].lower())
        return False


def request(query, params):
    m = parser_re.match(unicode(query, 'utf8'))
    if not m:
        return params

    from_lang, to_lang, query = m.groups()

    from_lang = is_valid_lang(from_lang)
    to_lang = is_valid_lang(to_lang)

    if not from_lang or not to_lang:
        return params

    params['url'] = url.format(from_lang=from_lang[1],
                               to_lang=to_lang[1],
                               query=query)
    params['query'] = query
    params['from_lang'] = from_lang
    params['to_lang'] = to_lang

    return params


def response(resp):
    results = []
    results.append({
        'url': escape(web_url.format(from_lang=resp.search_params['from_lang'][2],
                              to_lang=resp.search_params['to_lang'][2],
                              query=resp.search_params['query'])),
        'title': escape('[{0}-{1}] {2}'.format(resp.search_params['from_lang'][1],
                                                          resp.search_params['to_lang'][1],
                                                          resp.search_params['query'])),
        'content': escape(resp.json()['responseData']['translatedText'])
    })
    return results
