from urllib import urlencode
from HTMLParser import HTMLParser
from xpath import *

categories = ['dev']

search_url = 'http://vimeo.com/search?{query}'

Cookie = {
    'vuid':'918282893.1027205400'
    , 'ab_bs':'%7B%223%22%3A279%7D'
    , '__utma':'18302654.101#6140782.1388942090.1388942090.1388942090.1'
    , '__utmb':'18302654.1.10.1388942090'
    , '__utmc':'18302654'
    , '__utmz':'18#302654.1388942090.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
    , '__utml':'search'
}

#'vuid=918282893.1027205400& ab_bs=%7B%223%22%3A279%7D& player="scaling=1&volume=1"& __utma=18302654.101#6140782.1388942090.1388942090.1388942090.1& __utmb=18302654.1.10.1388942090& __utmc=18302654& __utmz=18#302654.1388942090.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)& __utmli=search'

def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q' :query}))
    print params['url']
    params['cookies'] = Cookie
    return params


def response(resp):
    results = []
    
    dom = html.fromstring(resp.text)

    if results_xpath:
        for result in dom.xpath(results_xpath):
            url = extract_url(result.xpath(url_xpath))

            title = extract_text(result.xpath(title_xpath)[0 ])
            content = extract_text(result.xpath(content_xpath)[0])
            results.append({'url': url, 'title': title, 'content': content})
    else:
        for url, title, content in zip(    
            map(extract_url, dom.xpath(url_xpath)), \
            map(extract_text, dom.xpath(title_xpath)), \
            map(extract_text, dom.xpath(content_xpath)), \
                ):
            results.append({'url': url, 'title': title, 'content': content})

    return results
