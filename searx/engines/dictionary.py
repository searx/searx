import re
from lxml import html
from searx.engines.xpath import extract_text
from searx.languages import language_codes

categories = []
url = 'http://dictzone.com/{from_lang}-{to_lang}-dictionary/{query}'
weight = 100

parser_re = re.compile(u'.*?([a-z]+)-([a-z]+) (.+)', re.I)
results_xpath = './/table[@id="r"]/tr'


def request(query, params):
    m = parser_re.match(unicode(query, 'utf8'))
    if not m:
        return params

    from_lang, to_lang, query = m.groups()

    if len(from_lang) == 2:
        lan = filter(lambda x: x[0][:2] == from_lang, language_codes)
        if lan:
            from_lang = lan[0][1].lower()
        else:
            return params

    if len(to_lang) == 2:
        lan = filter(lambda x: x[0][:2] == to_lang, language_codes)
        if lan:
            to_lang = lan[0][1].lower()
        else:
            return params

    params['url'] = url.format(from_lang=from_lang, to_lang=to_lang,query=query)
    params['from_lang'] = from_lang
    params['to_lang'] = to_lang
    params['query'] = query

    return params

def response(resp):
    results = []
    answers = []

    dom = html.fromstring(resp.text)

    for result in dom.xpath(results_xpath)[1:]:
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
            'answer': u'{0} - {1}'.format(
                from_result.text_content(),
                '; '.join(to_results)
            ),
            'url': url
        })

    return results


