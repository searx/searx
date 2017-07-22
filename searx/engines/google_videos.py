"""
 Google (Videos)

 @website     https://www.google.com
 @provide-api yes (https://developers.google.com/custom-search/)

 @using-api   no
 @results     HTML
 @stable      no
 @parse       url, title, content
"""

from datetime import date, timedelta
from json import loads
from lxml import html
from searx.engines.xpath import extract_text
from searx.url_utils import urlencode


# engine dependent config
categories = ['videos']
paging = True
safesearch = True
time_range_support = True
number_of_results = 10

search_url = 'https://www.google.com/search'\
    '?{query}'\
    '&tbm=vid'\
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
    for result in dom.xpath('//div[@class="g"]'):

        title = extract_text(result.xpath('.//h3/a'))
        url = result.xpath('.//h3/a/@href')[0]
        content = extract_text(result.xpath('.//span[@class="st"]'))

        # append result
        results.append({'url': url,
                        'title': title,
                        'content': content,
                        'thumbnail': '',
                        'template': 'videos.html'})

    return results
