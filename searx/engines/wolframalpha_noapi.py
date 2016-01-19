# WolframAlpha (Maths)
#
# @website     http://www.wolframalpha.com/
# @provide-api yes (http://api.wolframalpha.com/v2/)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       answer

from re import search, sub
from json import loads
from urllib import urlencode
from lxml import html
import HTMLParser

# search-url
url = 'http://www.wolframalpha.com/'
search_url = url + 'input/?{query}'

# xpath variables
scripts_xpath = '//script'
title_xpath = '//title'
failure_xpath = '//p[attribute::class="pfail"]'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'i': query}))

    return params


# get response from search-request
def response(resp):
    results = []
    line = None

    dom = html.fromstring(resp.text)
    scripts = dom.xpath(scripts_xpath)

    # the answer is inside a js function
    # answer can be located in different 'pods', although by default it should be in pod_0200
    possible_locations = ['pod_0200\.push\((.*)',
                          'pod_0100\.push\((.*)']

    # failed result
    if dom.xpath(failure_xpath):
        return results

    # get line that matches the pattern
    for pattern in possible_locations:
        for script in scripts:
            try:
                line = search(pattern, script.text_content()).group(1)
                break
            except AttributeError:
                continue
        if line:
            break

    if line:
        # extract answer from json
        answer = line[line.find('{'):line.rfind('}') + 1]
        try:
            answer = loads(answer)
        except Exception:
            answer = loads(answer.encode('unicode-escape'))
        answer = answer['stringified']

        # clean plaintext answer
        h = HTMLParser.HTMLParser()
        answer = h.unescape(answer.decode('unicode-escape'))
        answer = sub(r'\\', '', answer)

        results.append({'answer': answer})

    # user input is in first part of title
    title = dom.xpath(title_xpath)[0].text.encode('utf-8')
    result_url = request(title[:-16], {})['url']

    # append result
    results.append({'url': result_url,
                    'title': title.decode('utf-8')})

    return results
