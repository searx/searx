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
        content = result['repo'] + "<br />"
        
        lines = dict()
        for line, code in result['lines'].items():
            lines[int(line)] = code

        content = content + '<pre class="code-formatter"><table class="code">'
        for line, code in sorted(lines.items()):
            content = content + '<tr><td class="line-number" style="padding-right:5px;">' 
            content = content + str(line) + '</td><td class="code-snippet">' 
            # Replace every two spaces with ' &nbps;' to keep formatting while allowing the browser to break the line if necessary
            content = content + cgi.escape(code).replace('\t', '    ').replace('  ', '&nbsp; ').replace('  ', ' &nbsp;') 
            content = content + "</td></tr>"
            
        content = content + "</table></pre>"
        
        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content})

    # return results
    return results
