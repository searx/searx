# WolframAlpha (Maths)
#
# @website     http://www.wolframalpha.com/
#
# @using-api   no
# @results     HTML, JS
# @stable      no
# @parse       answer

import re
import json
from urllib import urlencode

# search-url
url = 'http://www.wolframalpha.com/'
search_url = url+'input/?{query}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'i': query}))

    return params


# get response from search-request
def response(resp):
    results = []
    
    # the answer is inside a js function
    # answer can be located in different 'pods', although by default it should be in pod_0200
    possible_locations = ['pod_0200\.push(.*)\n',
                          'pod_0100\.push(.*)\n']

    # get line that matches the pattern
    for pattern in possible_locations:
        try:
            line = re.search(pattern, resp.text).group(1)
            break
        except AttributeError:
            continue

    if not line:
        return results

    # extract answer from json
    answer = line[line.find('{') : line.rfind('}')+1]
    answer = json.loads(answer.encode('unicode-escape'))
    answer = answer['stringified'].decode('unicode-escape')

    results.append({'answer': answer})
    
    return results
