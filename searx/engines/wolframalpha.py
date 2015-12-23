"""
 WolframAlpha

 @website     http://www.wolframalpha.com/

 @using-api   yes
 @results     no c
 @stable      i guess so
 @parse       result
"""

import wolframalpha

# engine dependent config
paging = False

# search-url
# url = 'http://www.wolframalpha.com/'
# search_url = url+'input/?{query}'

client_id = '5952JX-X52L3VKWT8'
'''
# do search-request
def request(query, params):
    params['url'] = search_url.format(query=urlencode({'i': query}))
    print params

    return params


# get response from search-request
def response(resp):
    print resp

    dom = html.fromstring(resp.text)
    #resshit = dom.find_class('output pnt')
    #for shit in resshit:
        #print shit.text_content()
    results = []
    #results.append({'url': 'https://wikipedia.org', 'title': 'Wolfie, lol', 'content': 'es kwatro'})
    #print results
    #return results

    # parse results
    for result in dom.xpath(results_xpath):
        print result
        
        link = result.xpath(link_xpath)[0]
        href = urljoin(url, link.attrib.get('href'))
        title = escape(extract_text(link))
        content = escape(extract_text(result.xpath(content_xpath)))

        # append result
        results.append({'url': href,
                        'title': title,
                        'content': content})

    print results
    return results
'''
