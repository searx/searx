# Wolfram Alpha (Maths)
#
# @website     http://www.wolframalpha.com
# @provide-api yes (http://api.wolframalpha.com/v2/)
#
# @using-api   yes
# @results     XML
# @stable      yes
# @parse       result

from urllib import urlencode
from lxml import etree

# search-url
base_url = 'http://api.wolframalpha.com/v2/query'
search_url = base_url + '?appid={api_key}&{query}&format=plaintext'
site_url = 'http://www.wolframalpha.com/input/?{query}'
search_query = ''
api_key = ''

# xpath variables
failure_xpath = '/queryresult[attribute::success="false"]'
answer_xpath = '//pod[attribute::primary="true"]/subpod/plaintext'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'input': query}),
                                      api_key=api_key)

    # used in response
    global search_query
    search_query = query

    return params


# replace private user area characters to make text legible
def replace_pua_chars(text):
    pua_chars = {u'\uf74c': 'd',
                 u'\uf74d': u'\u212f',
                 u'\uf74e': 'i',
                 u'\uf7d9': '='}

    for k, v in pua_chars.iteritems():
        text = text.replace(k, v)

    return text


# get response from search-request
def response(resp):
    results = []

    search_results = etree.XML(resp.content)

    # return empty array if there are no results
    if search_results.xpath(failure_xpath):
        return []

    # parse answer
    answer = search_results.xpath(answer_xpath)
    if answer:
        answer = replace_pua_chars(answer[0].text)

        results.append({'answer': answer})

    # result url
    result_url = site_url.format(query=urlencode({'i': search_query}))

    # append result
    results.append({'url': result_url,
                    'title': search_query + ' - Wolfram|Alpha'})

    return results
