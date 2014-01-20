from urllib import urlencode
from HTMLParser import HTMLParser
from xpath import extract_text
from lxml import html

base_url = 'http://vimeo.com'
search_url = base_url + '/search?{query}'
url_xpath = None
content_xpath = None
title_xpath = None
results_xpath = ''
content_tpl = '<a href="{0}">  <img src="{2}"/> </a>'

# the cookie set by vimeo contains all the following values,
# but only __utma seems to be requiered
cookie = {
    #'vuid':'918282893.1027205400'
    # 'ab_bs':'%7B%223%22%3A279%7D'
     '__utma': '00000000.000#0000000.0000000000.0000000000.0000000000.0'
    # '__utmb':'18302654.1.10.1388942090'
    #, '__utmc':'18302654'
    #, '__utmz':'18#302654.1388942090.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'  # noqa
    #, '__utml':'search'
}


def request(query, params):
    params['url'] = search_url.format(query=urlencode({'q': query}))
    params['cookies'] = cookie
    return params


def response(resp):
    results = []
    dom = html.fromstring(resp.text)

    p = HTMLParser()

    for result in dom.xpath(results_xpath):
        url = base_url + result.xpath(url_xpath)[0]
        title = p.unescape(extract_text(result.xpath(title_xpath)))
        thumbnail = extract_text(result.xpath(content_xpath)[0])
        results.append({'url': url,
                        'title': title,
                        'content': content_tpl.format(url, title, thumbnail),
                        'template': 'videos.html',
                        'thumbnail': thumbnail})
    return results
