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
api_key = ''


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'input': query}),
                                      api_key=api_key)

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
    if search_results.xpath('/queryresult[attribute::success="false"]'):
        return []

    # parse result
    result = search_results.xpath('//pod[attribute::primary="true"]/subpod/plaintext')[0].text
    result = replace_pua_chars(result)

    # append result
    # TODO: shouldn't it bind the source too?
    results.append({'answer': result})

    # return results
    return results
