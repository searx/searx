"""
 Gigablast (Web)

 @website     https://gigablast.com
 @provide-api yes (https://gigablast.com/api.html)

 @using-api   yes
 @results     XML
 @stable      yes
 @parse       url, title, content
"""
# pylint: disable=missing-function-docstring, invalid-name

from time import time
from json import loads
from searx.url_utils import urlencode

# engine dependent config
categories = ['general']
paging = True
number_of_results = 10
language_support = True
safesearch = True

# search-url

base_url = 'https://gigablast.com/'

# do search-request
def request(query, params):  # pylint: disable=unused-argument

    # see API http://www.gigablast.com/api.html#/search
    # Take into account, that the API has some quirks ..

    query_args = dict(
        c = 'main'
        , n = number_of_results
        , format = 'json'
        , q = query
        # The gigablast HTTP client sends a random number and a nsga argument
        # (the values don't seem to matter)
        , rand = int(time() * 1000)
        , nsga = int(time() * 1000)
    )

    page_no = (params['pageno'] - 1)
    if page_no:
        # API quirk; adds +2 to the number_of_results
        offset = (params['pageno'] - 1) * number_of_results
        query_args['s'] = offset

    if params['language'] and params['language'] != 'all':
        query_args['qlangcountry'] = params['language']
        query_args['qlang'] = params['language'].split('-')[0]

    if params['safesearch'] >= 1:
        query_args['ff'] = 1

    search_url = 'search?' + urlencode(query_args)
    params['url'] = base_url + search_url

    return params

# get response from search-request
def response(resp):
    results = []

    response_json = loads(resp.text)
    for result in response_json['results']:
        # see "Example JSON Output (&format=json)"
        # at http://www.gigablast.com/api.html#/search

        # sort out meaningless result

        title = result.get('title')
        if len(title) < 2:
            continue

        url = result.get('url')
        if len(url) < 9:
            continue

        content = result.get('sum')
        if len(content) < 5:
            continue

        # extend fields

        subtitle = result.get('title')
        if len(subtitle) > 3:
            title += " - " + subtitle

        results.append(dict(
            url = url
            , title = title
            , content = content
        ))

    return results
