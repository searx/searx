# SPDX-License-Identifier: AGPL-3.0-or-later
"""
 Gigablast (Web)
"""
# pylint: disable=missing-function-docstring, invalid-name

import re
from json import loads, JSONDecodeError
from urllib.parse import urlencode
from searx.exceptions import SearxEngineResponseException
from searx.poolrequests import get

# about
about = {
    "website": 'https://www.gigablast.com',
    "wikidata_id": 'Q3105449',
    "official_api_documentation": 'https://gigablast.com/api.html',
    "use_official_api": True,
    "require_api_key": False,
    "results": 'JSON',
}

# engine dependent config
categories = ['general']
collections = 'main'
search_type = ''
fast = 0
# gigablast's pagination is totally damaged, don't use it
paging = False
safesearch = True

# search-url
base_url = 'https://gigablast.com'

# ugly hack: gigablast requires a random extra parameter which can be extracted
# from the source code of the gigablast HTTP client
extra_param = ''
extra_param_path='/search?c=main&qlangcountry=en-us&q=south&s=10'

_wait_for_results_msg = 'Loading results takes too long. Please enable fast option in gigablast engine.'

def parse_extra_param(text):

    # example:
    #
    # var uxrl='/search?c=main&qlangcountry=en-us&q=south&s=10&rand=1590740241635&n';
    # uxrl=uxrl+'sab=730863287';
    #
    # extra_param --> "rand=1590740241635&nsab=730863287"

    global extra_param  # pylint: disable=global-statement
    re_var= None
    for line in text.splitlines():
        if re_var is None and extra_param_path in line:
            var = line.split("=")[0].split()[1]  # e.g. var --> 'uxrl'
            re_var = re.compile(var + "\\s*=\\s*" + var + "\\s*\\+\\s*'" + "(.*)" + "'(.*)")
            extra_param = line.split("'")[1][len(extra_param_path):]
            continue
        if re_var is not None and re_var.search(line):
            extra_param += re_var.search(line).group(1)
            break

def init(engine_settings=None):  # pylint: disable=unused-argument
    parse_extra_param(get(base_url + extra_param_path).text)


# do search-request
def request(query, params):  # pylint: disable=unused-argument

    # see API http://www.gigablast.com/api.html#/search
    # Take into account, that the API has some quirks ..
    query_args = {
        'c': collections,
        'format': 'json',
        'q': query,
        'dr': 1 ,
        'showgoodimages': 0,
        'fast': fast,
    }

    if search_type != '':
        query_args['searchtype'] = search_type

    if params['language'] and params['language'] != 'all':
        query_args['qlangcountry'] = params['language']
        query_args['qlang'] = params['language'].split('-')[0]

    if params['safesearch'] >= 1:
        query_args['ff'] = 1

    search_url = '/search?' + urlencode(query_args)
    params['url'] = base_url + search_url + extra_param

    return params

# get response from search-request
def response(resp):
    results = []

    try:
        response_json = loads(resp.text)
    except JSONDecodeError as e:
        if 'Waiting for results' in resp.text:
            raise SearxEngineResponseException(message=_wait_for_results_msg)  # pylint: disable=raise-missing-from
        raise e


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
        if len(subtitle) > 3 and subtitle != title:
            title += " - " + subtitle

        results.append(dict(
            url = url
            , title = title
            , content = content
        ))

    return results
