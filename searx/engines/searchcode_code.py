"""
 Searchcode (It)

 @website     https://searchcode.com/
 @provide-api yes (https://searchcode.com/api/)

 @using-api   yes
 @results     JSON
 @stable      yes
 @parse       url, title, content
"""

from json import loads
from searx.url_utils import urlencode


# engine dependent config
categories = ['it']
paging = True

# search-url
url = 'https://searchcode.com/'
search_url = url + 'api/codesearch_I/?{query}&p={pageno}'

# special code-endings which are not recognised by the file ending
code_endings = {'cs': 'c#',
                'h': 'c',
                'hpp': 'cpp',
                'cxx': 'cpp'}


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}), pageno=params['pageno'] - 1)

    return params


# get response from search-request
def response(resp):
    results = []

    search_results = loads(resp.text)

    # parse results
    for result in search_results.get('results', []):
        href = result['url']
        title = "" + result['name'] + " - " + result['filename']
        repo = result['repo']

        lines = dict()
        for line, code in result['lines'].items():
            lines[int(line)] = code

        code_language = code_endings.get(
            result['filename'].split('.')[-1].lower(),
            result['filename'].split('.')[-1].lower())

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': '',
                        'repository': repo,
                        'codelines': sorted(lines.items()),
                        'code_language': code_language,
                        'template': 'code.html'})

    # return results
    return results
