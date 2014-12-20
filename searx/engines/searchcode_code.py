## Searchcode (It)
#
# @website     https://searchcode.com/
# @provide-api yes (https://searchcode.com/api/)
#
# @using-api   yes
# @results     JSON
# @stable      yes
# @parse       url, title, content

from urllib import urlencode
from json import loads
import cgi
import re

# engine dependent config
categories = ['it']
paging = True

# search-url
url = 'https://searchcode.com/'
search_url = url+'api/codesearch_I/?{query}&p={pageno}'

code_endings = {'c': 'c',
                'css': 'css',
                'cpp': 'cpp',
                'c++': 'cpp',
                'h': 'c',
                'html': 'html',
                'hpp': 'cpp',
                'js': 'js',
                'lua': 'lua',
                'php': 'php',
                'py': 'python'}


# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}),
                                      pageno=params['pageno']-1)

    return params


# get response from search-request
def response(resp):
    results = []
    
    search_results = loads(resp.text)

    # parse results
    for result in search_results['results']:
        href = result['url']
        title = "" + result['name'] + " - " + result['filename']
        repo = result['repo']
        
        lines = dict()
        for line, code in result['lines'].items():
            lines[int(line)] = code

        code_language = code_endings.get(result['filename'].split('.')[-1].lower(), None)

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
