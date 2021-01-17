# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Google (Videos)
"""

from datetime import date, timedelta
from dateutil import parser
from urllib.parse import urlencode
from lxml import html
from searx.utils import extract_text, eval_xpath, eval_xpath_list, eval_xpath_getindex
import re

# about
about = {
    "website": 'https://www.google.com',
    "wikidata_id": 'Q219885',
    "official_api_documentation": 'https://developers.google.com/custom-search/',
    "use_official_api": False,
    "require_api_key": False,
    "results": 'HTML',
}

# engine dependent config
categories = ['videos']
paging = True
safesearch = True
time_range_support = True
number_of_results = 10

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=vid&hl=en-US&lr=lang_en'\
    '&{search_options}'
time_range_attr = "qdr:{range}"
time_range_custom_attr = "cdr:1,cd_min:{start},cd_max{end}"
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}


# do search-request
def request(query, params):
    search_options = {
        'ijn': params['pageno'] - 1,
        'start': (params['pageno'] - 1) * number_of_results
    }

    if params['time_range'] in time_range_dict:
        search_options['tbs'] = time_range_attr.format(range=time_range_dict[params['time_range']])
    elif params['time_range'] == 'year':
        now = date.today()
        then = now - timedelta(days=365)
        start = then.strftime('%m/%d/%Y')
        end = now.strftime('%m/%d/%Y')
        search_options['tbs'] = time_range_custom_attr.format(start=start, end=end)

    if safesearch and params['safesearch']:
        search_options['safe'] = 'on'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      search_options=urlencode(search_options))

    return params


# get response from search-request
def response(resp):
    results = []

    dom = html.fromstring(resp.text)

    # parse results
    for result in eval_xpath_list(dom, '//div[@class="g"]'):

        result_data = {'url': eval_xpath_getindex(result, './/a/@href', 0),
                       'title': extract_text(eval_xpath(result, './/h3')),
                       'content': extract_text(eval_xpath(result, './/span[@class="aCOpRe"]')),
                       'length': extract_text(eval_xpath(result, './/div[@class="ij69rd UHe5G"]')),
                       'thumbnail': '',
                       'template': 'videos.html'}

        author_and_date = extract_text(eval_xpath(result, './/div[@class="fG8Fp uo4vr"]'))

        # Parse author
        authors = re.findall('Uploaded by (.*)', author_and_date)
        if len(authors) > 0:
            result_data['author'] = authors[0]

        # Parse publish date
        try:
            result_data['date'] = parser.parse(author_and_date.split('·')[0])
        except parser.ParserError:
            pass

        # Parse thumbnail
        ids = eval_xpath_list(result, ".//img/@id")
        if len(ids) > 0:
            i = ids[0]
            tmp = re.findall("(\w+)=\\'([^\\']*)\\';var (\w+)=\[\\'" + i + "\\'\];_setImagesSrc\(\\3,\\1\);", resp.text)
            if len(tmp) > 0:
                result_data['thumbnail'] = tmp[0][1].replace("\\x3d", "=")
            else:
                tmp = re.findall("\\\"" + i + "\\\":\\\"([^\\\"]+)\\\"", resp.text)
                if len(tmp) > 0:
                    result_data['thumbnail'] = tmp[0].replace("\\u003d", "=")

        results.append(result_data)

    return results
