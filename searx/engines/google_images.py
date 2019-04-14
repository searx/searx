"""
 Google (Images)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   no
 @results     HTML chunks with JSON inside
 @stable      no
 @parse       url, title, img_src
"""

from datetime import date, timedelta
from lxml import html
from searx.url_utils import urlencode, urlparse, parse_qs


# engine dependent config
categories = ['images']
paging = True
safesearch = True
time_range_support = True
number_of_results = 100

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=isch'\
    '&gbv=1'\
    '&sa=G'\
    '&{search_options}'
time_range_attr = "qdr:{range}"
time_range_custom_attr = "cdr:1,cd_min:{start},cd_max{end}"
time_range_dict = {'day': 'd',
                   'week': 'w',
                   'month': 'm'}


# do search-request
def request(query, params):
    search_options = {
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
        search_options['safe'] = 'active'

    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      search_options=urlencode(search_options))

    return params


# get response from search-request
def response(resp):
    dom = html.fromstring(resp.text)

    results = []
    for element in dom.xpath('//div[@id="search"] //td'):
        link = element.xpath('./a')[0]

        google_url = urlparse(link.xpath('.//@href')[0])
        query = parse_qs(google_url.query)
        source_url = next(iter(query.get('q', [])), None)

        title_parts = element.xpath('./cite//following-sibling::*/text()')
        title_parts.extend(element.xpath('./cite//following-sibling::text()')[:-1])

        result = {
            'title': ''.join(title_parts),
            'content': '',
            'template': 'images.html',
            'url': source_url,
            'img_src': source_url,
            'thumbnail_src': next(iter(link.xpath('.//img //@src')), None)
        }

        if not source_url or not result['thumbnail_src']:
            continue

        results.append(result)
    return results
