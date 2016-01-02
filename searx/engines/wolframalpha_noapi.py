# WolframAlpha (Maths)
#
# @website     http://www.wolframalpha.com/
# @provide-api yes (http://api.wolframalpha.com/v2/)
#
# @using-api   no
# @results     HTML
# @stable      no
# @parse       answer

from re import search
from json import loads
from urllib import urlencode

# search-url
url = 'http://www.wolframalpha.com/'
search_url = url+'input/?{query}'
search_query = ''


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'i': query}))

    # used in response
    global search_query
    search_query = query

    return params


# get response from search-request
def response(resp):
    results = []
    webpage = resp.text
    line = None

    # the answer is inside a js function
    # answer can be located in different 'pods', although by default it should be in pod_0200
    possible_locations = ['pod_0200\.push(.*)\n',
                          'pod_0100\.push(.*)\n']

    # get line that matches the pattern
    for pattern in possible_locations:
        try:
            line = search(pattern, webpage).group(1)
            break
        except AttributeError:
            continue

    if line:
        # extract answer from json
        answer = line[line.find('{'):line.rfind('}')+1]
        answer = loads(answer.encode('unicode-escape'))
        answer = answer['stringified'].decode('unicode-escape')

        results.append({'answer': answer})

    # failed result
    elif search('pfail', webpage):
        return results

    # append result
    results.append({'url': request(search_query, {})['url'],
                    'title': search_query + ' - Wolfram|Alpha'})

    return results
