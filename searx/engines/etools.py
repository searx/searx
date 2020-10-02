"""
 eTools (Web)

 @website      https://www.etools.ch
 @provide-api  no
 @using-api    no
 @results      HTML
 @stable       no (HTML can change)
 @parse        url, title, content
"""

from lxml import html
from urllib.parse import quote
from searx.utils import extract_text, eval_xpath

categories = ['general']
paging = False
language_support = False
safesearch = True

base_url = 'https://www.etools.ch'
search_path = '/searchAdvancedSubmit.do'\
    '?query={search_term}'\
    '&pageResults=20'\
    '&safeSearch={safesearch}'


def request(query, params):
    if params['safesearch']:
        safesearch = 'true'
    else:
        safesearch = 'false'

    params['url'] = base_url + search_path.format(search_term=quote(query), safesearch=safesearch)

    return params


def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    for result in eval_xpath(dom, '//table[@class="result"]//td[@class="record"]'):
        url = eval_xpath(result, './a/@href')[0]
        title = extract_text(eval_xpath(result, './a//text()'))
        content = extract_text(eval_xpath(result, './/div[@class="text"]//text()'))

        results.append({'url': url,
                        'title': title,
                        'content': content})

    return results
