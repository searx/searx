import re
from urlparse import urljoin
from lxml import html
from cgi import escape
from searx.engines.xpath import extract_text
from searx.languages import language_codes

categories = ['general']
url = 'http://dictzone.com/{from_lang}-{to_lang}-dictionary/{query}'
weight = 100

parser_re = re.compile(u'.*?([a-z]+)-([a-z]+) (.+)', re.I)
results_xpath = './/table[@id="r"]/tr'


def is_valid_lang(lang):
    is_abbr = (len(lang) == 2)
    if is_abbr:
        for l in language_codes:
            if l[0][:2] == lang.lower():
                return (True, l[1].lower())
        return False
    else:
        for l in language_codes:
            if l[1].lower() == lang.lower():
                return (True, l[1].lower())
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

    params['url'] = url.format(from_lang=from_lang[1], to_lang=to_lang[1],query=query)
    params['from_lang'] = from_lang[1]
    params['to_lang'] = to_lang[1]
    params['query'] = query

    return params

def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for k, result in enumerate(dom.xpath(results_xpath)[1:]):
        try:
            from_result, to_results_raw = result.xpath('./td')
        except:
            continue

        to_results = []
        for to_result in to_results_raw.xpath('./p/a'):
            t = to_result.text_content()
            if t.strip():
                to_results.append(to_result.text_content())

        results.append({
            'url': urljoin(resp.url, '?%d' % k),
            'title': escape(from_result.text_content()),
            'content': escape('; '.join(to_results))
        })

    return results


