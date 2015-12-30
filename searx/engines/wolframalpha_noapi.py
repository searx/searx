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
from lxml import html
from searx.engines.xpath import extract_text

# search-url
url = 'http://www.wolframalpha.com/'
search_url = url+'input/?{query}'


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'i': query}))

    return params


# tries to find answer under the pattern given
def extract_answer(script_list, pattern):
    answer = None

    # get line that matches the pattern
    for script in script_list:
        try:
            line = re.search(pattern, script.text_content()).group(1)
        except AttributeError:
            continue

        # extract answer from json
        answer = line[line.find('{') : line.rfind('}')+1]
        answer = json.loads(answer.encode('unicode-escape'))
        answer = answer['stringified'].decode('unicode-escape')

    return answer


# get response from search-request
def response(resp):

    dom = html.fromstring(resp.text)

    # the answer is inside a js script
    scripts = dom.xpath('//script')

    results = []

    # answer can be located in different 'pods', although by default it should be in pod_0200
    answer = extract_answer(scripts, 'pod_0200\.push(.*)\n')
    if not answer:
        answer = extract_answer(scripts, 'pod_0100\.push(.*)\n')
        if answer:
            results.append({'answer': answer})
    else:
        results.append({'answer': answer})
    
    return results
