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
from re import search

# search-url
base_url = 'http://api.wolframalpha.com/v2/query'
search_url = base_url + '?appid={api_key}&{query}&format=plaintext'
site_url = 'http://www.wolframalpha.com/input/?{query}'
api_key = ''  # defined in settings.yml

# xpath variables
failure_xpath = '/queryresult[attribute::success="false"]'
answer_xpath = '//pod[attribute::primary="true"]/subpod/plaintext'
input_xpath = '//pod[starts-with(attribute::title, "Input")]/subpod/plaintext'


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
    if search_results.xpath(failure_xpath):
        return []

    # parse answers
    answers = search_results.xpath(answer_xpath)
    if answers:
        for answer in answers:
            answer = replace_pua_chars(answer.text)

            results.append({'answer': answer})

    # if there's no input section in search_results, check if answer has the input embedded (before their "=" sign)
    try:
        query_input = search_results.xpath(input_xpath)[0].text
    except IndexError:
        query_input = search(u'([^\uf7d9]+)', answers[0].text).group(1)

    # append link to site
    result_url = site_url.format(query=urlencode({'i': query_input.encode('utf-8')}))
    results.append({'url': result_url,
                    'title': query_input + " - Wolfram|Alpha"})

    return results
